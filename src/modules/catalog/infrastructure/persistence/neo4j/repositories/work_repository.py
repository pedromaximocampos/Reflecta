from collections.abc import Mapping
from typing import Any

from neo4j import AsyncTransaction
from neo4j.exceptions import ConstraintError

from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.domain.exceptions.work_exceptions import WorkAlreadyExistsError
from src.modules.catalog.domain.ports.repositories.iwork_repository import IWorkRepository
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

    async def get_work_by_slug(self, slug: str) -> Work | None:
        result = await self._transaction.run(
            "MATCH (work:Work {slug: $slug}) RETURN work",
            slug=slug,
        )
        record = await result.single()
        return None if record is None else self._work_mapper.to_entity(record["work"])

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
