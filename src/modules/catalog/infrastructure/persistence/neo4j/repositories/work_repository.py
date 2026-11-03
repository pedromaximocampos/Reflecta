from collections.abc import Mapping
from datetime import datetime
from typing import Any

from neo4j import AsyncTransaction
from neo4j.exceptions import ConstraintError

from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.domain.exceptions.work_exceptions import WorkAlreadyExistsError
from src.modules.catalog.domain.value_objects.catalog_status import CatalogStatus
from src.modules.catalog.domain.ports.repositories.iwork_repository import (
    IWorkRepository,
    WorkCatalogRecord,
)
from src.modules.catalog.public.work_id import WorkId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class WorkRepository(IWorkRepository):
    def __init__(
        self,
        transaction: AsyncTransaction,
        work_mapper: IMapper[Mapping[str, Any], Work],
        author_mapper: IMapper[Mapping[str, Any], Author],
    ) -> None:
        self._transaction = transaction
        self._work_mapper = work_mapper
        self._author_mapper = author_mapper

    async def get_work_by_id(self, work_id: WorkId) -> Work | None:
        result = await self._transaction.run(
            "MATCH (work:Work {work_id: $work_id}) RETURN work",
            work_id=work_id.value,
        )
        record = await result.single()
        return None if record is None else self._work_mapper.to_entity(record["work"])

    async def get_work_with_author_by_id(
        self,
        work_id: WorkId,
    ) -> WorkCatalogRecord | None:
        result = await self._transaction.run(
            """
            MATCH (work:Work {work_id: $work_id})-[:WRITTEN_BY]->(author:Author)
            OPTIONAL MATCH (passage:Passage)-[:BELONGS_TO]->(work)
            WITH work,
                 author,
                 count(passage) AS passage_count,
                 count(CASE WHEN passage.status = 'ACTIVE' THEN 1 END)
                     AS active_passage_count
            RETURN work,
                   author,
                   passage_count,
                   active_passage_count,
                   passage_count - active_passage_count
                       AS inactive_passage_count
            """,
            work_id=work_id.value,
        )
        record = await result.single()
        if record is None:
            return None
        return self._to_catalog_record(record)

    async def get_work_by_slug(self, slug: str) -> Work | None:
        result = await self._transaction.run(
            "MATCH (work:Work {slug: $slug}) RETURN work",
            slug=slug,
        )
        record = await result.single()
        return None if record is None else self._work_mapper.to_entity(record["work"])

    async def list_works(self) -> list[WorkCatalogRecord]:
        result = await self._transaction.run(
            """
            MATCH (work:Work)-[:WRITTEN_BY]->(author:Author)
            OPTIONAL MATCH (passage:Passage)-[:BELONGS_TO]->(work)
            WITH work,
                 author,
                 count(passage) AS passage_count,
                 count(CASE WHEN passage.status = 'ACTIVE' THEN 1 END)
                     AS active_passage_count
            RETURN work,
                   author,
                   passage_count,
                   active_passage_count,
                   passage_count - active_passage_count
                       AS inactive_passage_count
            ORDER BY work.created_at DESC, work.work_id
            """
        )
        return [
            self._to_catalog_record(record)
            async for record in result
        ]

    def _to_catalog_record(self, record: Mapping[str, Any]) -> WorkCatalogRecord:
        active_passage_count = int(record["active_passage_count"])
        work = self._work_mapper.to_entity(record["work"])
        work.status = (
            CatalogStatus.ACTIVE
            if active_passage_count > 0
            else CatalogStatus.INACTIVE
        )
        return WorkCatalogRecord(
            work=work,
            author=self._author_mapper.to_entity(record["author"]),
            passage_count=int(record["passage_count"]),
            active_passage_count=active_passage_count,
            inactive_passage_count=int(record["inactive_passage_count"]),
        )

    async def update_work(self, work: Work) -> Work:
        result = await self._transaction.run(
            """
            MATCH (stored_work:Work {work_id: $work_id})
            SET stored_work = $properties
            RETURN stored_work AS work
            """,
            work_id=work.id.value,
            properties=dict(self._work_mapper.to_model(work)),
        )
        record = await result.single(strict=True)
        return self._work_mapper.to_entity(record["work"])

    async def sync_status_from_active_passages(
        self,
        work_id: WorkId,
        updated_at: datetime,
    ) -> Work:
        result = await self._transaction.run(
            """
            MATCH (work:Work {work_id: $work_id})
            OPTIONAL MATCH (passage:Passage {status: 'ACTIVE'})-[:BELONGS_TO]->(work)
            WITH work,
                 CASE WHEN count(passage) > 0 THEN 'ACTIVE' ELSE 'INACTIVE' END
                     AS next_status
            WITH work, next_status, work.status <> next_status AS status_changed
            SET work.status = next_status,
                work.updated_at = CASE
                    WHEN status_changed THEN $updated_at
                    ELSE work.updated_at
                END
            RETURN work
            """,
            work_id=work_id.value,
            updated_at=updated_at,
        )
        record = await result.single(strict=True)
        return self._work_mapper.to_entity(record["work"])

    async def create_work(self, work: Work, author: Author) -> tuple[Work, Author]:
        try:
            result = await self._transaction.run(
                """
                MERGE (stored_author:Author {normalized_name: $normalized_name})
                ON CREATE SET stored_author = $author_properties
                CREATE (created_work:Work)
                SET created_work = $work_properties
                CREATE (created_work)-[:WRITTEN_BY]->(stored_author)
                RETURN created_work AS work, stored_author AS author
                """,
                normalized_name=author.normalized_name,
                author_properties=dict(self._author_mapper.to_model(author)),
                work_properties=dict(self._work_mapper.to_model(work)),
            )
            record = await result.single(strict=True)
            return (
                self._work_mapper.to_entity(record["work"]),
                self._author_mapper.to_entity(record["author"]),
            )
        except ConstraintError as error:
            raise WorkAlreadyExistsError(work.slug) from error
