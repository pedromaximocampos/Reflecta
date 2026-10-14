from collections.abc import Mapping, Sequence
from typing import Any

from neo4j import AsyncTransaction

from src.modules.catalog.domain.entities.passage import Passage
from src.modules.catalog.domain.ports.repositories import IPassageRepository
from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class PassageRepository(IPassageRepository):
    def __init__(
        self,
        transaction: AsyncTransaction,
        mapper: IMapper[Mapping[str, Any], Passage],
    ) -> None:
        self._transaction = transaction
        self._mapper = mapper

    async def get_by_id(self, passage_id: PassageId) -> Passage | None:
        result = await self._transaction.run(
            """
            MATCH (passage:Passage {passage_id: $passage_id})
            OPTIONAL MATCH (passage)-[relevance:RELATES_TO]->(theme:Theme)
            WITH passage, collect(
                CASE WHEN theme IS NULL THEN NULL ELSE {
                    theme_id: theme.theme_id,
                    confidence: relevance.confidence
                } END
            ) AS raw_themes
            RETURN passage,
                   [item IN raw_themes WHERE item IS NOT NULL] AS themes
            """,
            passage_id=passage_id.value,
        )
        record = await result.single()
        return None if record is None else self._record_to_entity(record)

    async def list_passages(
        self,
        *,
        status: CatalogStatus | None = None,
        work_id: WorkId | None = None,
        ingestion_id: WorkIngestionId | None = None,
    ) -> list[Passage]:
        result = await self._transaction.run(
            """
            MATCH (passage:Passage)
            WHERE ($status IS NULL OR passage.status = $status)
              AND ($work_id IS NULL OR passage.work_id = $work_id)
              AND ($ingestion_id IS NULL OR passage.ingestion_id = $ingestion_id)
            OPTIONAL MATCH (passage)-[relevance:RELATES_TO]->(theme:Theme)
            WITH passage, collect(
                CASE WHEN theme IS NULL THEN NULL ELSE {
                    theme_id: theme.theme_id,
                    confidence: relevance.confidence
                } END
            ) AS raw_themes
            RETURN passage,
                   [item IN raw_themes WHERE item IS NOT NULL] AS themes
            ORDER BY passage.priority DESC, passage.created_at, passage.passage_id
            """,
            status=status.value if status is not None else None,
            work_id=work_id.value if work_id is not None else None,
            ingestion_id=(
                ingestion_id.value if ingestion_id is not None else None
            ),
        )
        return [self._record_to_entity(record) async for record in result]

    async def create(self, passage: Passage) -> Passage:
        await self._ensure_work_and_themes(
            passage.work_id,
            [theme.theme_id.value for theme in passage.themes],
            active_only=True,
        )
        theme_links = self._theme_links(passage)
        result = await self._transaction.run(
            """
            MATCH (work:Work {work_id: $work_id})
            CREATE (passage:Passage)
            SET passage = $properties
            CREATE (passage)-[:BELONGS_TO]->(work)
            WITH passage
            UNWIND $themes AS theme_link
            MATCH (theme:Theme {theme_id: theme_link.theme_id, is_active: true})
            CREATE (passage)-[:RELATES_TO {
                confidence: theme_link.confidence,
                source: $source
            }]->(theme)
            RETURN passage
            """,
            work_id=passage.work_id.value,
            properties=dict(self._mapper.to_model(passage)),
            themes=theme_links,
            source=passage.source,
        )
        record = await result.single(strict=True)
        return self._mapper.to_entity(
            {**dict(record["passage"]), "themes": theme_links}
        )

    async def update(self, passage: Passage) -> Passage:
        await self._ensure_work_and_themes(
            passage.work_id,
            [theme.theme_id.value for theme in passage.themes],
            active_only=False,
        )
        theme_links = self._theme_links(passage)
        result = await self._transaction.run(
            """
            MATCH (stored:Passage {passage_id: $passage_id})
            SET stored = $properties
            WITH stored
            OPTIONAL MATCH (stored)-[old:RELATES_TO]->(:Theme)
            DELETE old
            WITH DISTINCT stored
            UNWIND $themes AS theme_link
            MATCH (theme:Theme {theme_id: theme_link.theme_id})
            CREATE (stored)-[:RELATES_TO {
                confidence: theme_link.confidence,
                source: $source
            }]->(theme)
            RETURN stored AS passage
            """,
            passage_id=passage.id.value,
            properties=dict(self._mapper.to_model(passage)),
            themes=theme_links,
            source=passage.source,
        )
        record = await result.single(strict=True)
        return self._mapper.to_entity(
            {**dict(record["passage"]), "themes": theme_links}
        )

    async def count_pending_by_ingestion(
        self,
        ingestion_id: WorkIngestionId,
    ) -> int:
        result = await self._transaction.run(
            """
            MATCH (passage:Passage {
                ingestion_id: $ingestion_id,
                status: 'PENDING_REVIEW'
            })
            RETURN count(passage) AS pending
            """,
            ingestion_id=ingestion_id.value,
        )
        record = await result.single(strict=True)
        return int(record["pending"])

    async def replace_ai_candidates_for_chunk(
        self,
        *,
        ingestion_id: WorkIngestionId,
        work_id: WorkId,
        chunk_id: str,
        passages: Sequence[Passage],
    ) -> None:
        self._validate_candidates(ingestion_id, work_id, chunk_id, passages)
        theme_ids = sorted(
            {theme.theme_id.value for passage in passages for theme in passage.themes}
        )
        await self._ensure_work_and_themes(
            work_id,
            theme_ids,
            active_only=True,
        )

        delete_result = await self._transaction.run(
            """
            MATCH (passage:Passage {
                ingestion_id: $ingestion_id,
                source_chunk_id: $chunk_id,
                source: 'ai'
            })
            WHERE passage.status = 'PENDING_REVIEW'
            DETACH DELETE passage
            """,
            ingestion_id=ingestion_id.value,
            chunk_id=chunk_id,
        )
        await delete_result.consume()
        if not passages:
            return

        items = [
            {
                "properties": dict(self._mapper.to_model(passage)),
                "themes": [
                    {
                        "theme_id": theme.theme_id.value,
                        "confidence": theme.confidence,
                    }
                    for theme in passage.themes
                ],
            }
            for passage in passages
        ]
        result = await self._transaction.run(
            """
            MATCH (work:Work {work_id: $work_id})
            UNWIND $items AS item
            MERGE (passage:Passage {source_key: item.properties.source_key})
            ON CREATE SET passage = item.properties
            MERGE (passage)-[:BELONGS_TO]->(work)
            WITH passage, item
            UNWIND item.themes AS theme_link
            MATCH (theme:Theme {theme_id: theme_link.theme_id, is_active: true})
            MERGE (passage)-[relevance:RELATES_TO]->(theme)
            SET relevance.confidence = CASE
                WHEN relevance.confidence IS NULL
                  OR theme_link.confidence > relevance.confidence
                THEN theme_link.confidence
                ELSE relevance.confidence
            END,
            relevance.source = 'ai'
            RETURN count(DISTINCT passage) AS resolved
            """,
            work_id=work_id.value,
            items=items,
        )
        record = await result.single(strict=True)
        if record["resolved"] != len(passages):
            raise RuntimeError("Not all AI passage candidates were persisted.")

    async def _ensure_work_and_themes(
        self,
        work_id: WorkId,
        theme_ids: list[str],
        *,
        active_only: bool,
    ) -> None:
        work_result = await self._transaction.run(
            "MATCH (work:Work {work_id: $work_id}) RETURN count(work) AS count",
            work_id=work_id.value,
        )
        work_record = await work_result.single(strict=True)
        if work_record["count"] != 1:
            raise LookupError(f"Work '{work_id.value}' was not found in the catalog.")
        if not theme_ids:
            return

        theme_result = await self._transaction.run(
            """
            MATCH (theme:Theme)
            WHERE theme.theme_id IN $theme_ids
              AND (NOT $active_only OR theme.is_active = true)
            RETURN collect(theme.theme_id) AS found_theme_ids
            """,
            theme_ids=theme_ids,
            active_only=active_only,
        )
        theme_record = await theme_result.single(strict=True)
        if set(theme_record["found_theme_ids"]) != set(theme_ids):
            qualifier = "active" if active_only else "available"
            raise LookupError(
                f"One or more selected themes are not {qualifier}."
            )

    @staticmethod
    def _validate_candidates(
        ingestion_id: WorkIngestionId,
        work_id: WorkId,
        chunk_id: str,
        passages: Sequence[Passage],
    ) -> None:
        if not chunk_id.strip():
            raise ValueError("Chunk ID must not be empty.")
        for passage in passages:
            if (
                passage.ingestion_id != ingestion_id
                or passage.work_id != work_id
                or passage.source_chunk_id != chunk_id
            ):
                raise ValueError("Passage candidate ownership is inconsistent.")

    def _record_to_entity(self, record: Mapping[str, Any]) -> Passage:
        return self._mapper.to_entity(
            {
                **dict(record["passage"]),
                "themes": list(record["themes"]),
            }
        )

    @staticmethod
    def _theme_links(passage: Passage) -> list[dict[str, Any]]:
        return [
            {
                "theme_id": theme.theme_id.value,
                "confidence": theme.confidence,
            }
            for theme in passage.themes
        ]
