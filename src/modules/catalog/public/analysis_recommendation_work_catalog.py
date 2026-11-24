import asyncio
import logging

from src.modules.catalog.application.exceptions import WorkCoverStorageError
from src.modules.catalog.application.ports.storage import IWorkCoverStorage
from src.modules.catalog.domain.ports.repositories.iwork_repository import (
    WorkCatalogRecord,
)
from src.modules.catalog.domain.ports.unit_of_work import ICatalogGraphUnitOfWork
from src.modules.catalog.public.recommendation_work import (
    RecommendationWork,
    RecommendationWorkPage,
)


_LOGGER = logging.getLogger(__name__)
_MAX_PAGE_SIZE = 24
_MAX_LOOKUP_SIZE = 24


class AnalysisRecommendationWorkCatalog:
    """Read-only catalog facade for recommendation and discovery use cases.

    The facade deliberately resolves managed cover keys inside Catalog so other
    modules never receive S3 object keys or depend on storage infrastructure.
    """

    def __init__(
        self,
        uow: ICatalogGraphUnitOfWork,
        cover_storage: IWorkCoverStorage,
    ) -> None:
        self._uow = uow
        self._cover_storage = cover_storage

    async def find_by_ids(
        self,
        work_ids: tuple[str, ...],
    ) -> tuple[RecommendationWork, ...]:
        self._validate_work_ids(work_ids)
        if not work_ids:
            return ()

        records = await self._list_records()
        record_by_id = {record.work.id.value: record for record in records}
        selected = tuple(
            record_by_id[work_id]
            for work_id in work_ids
            if work_id in record_by_id
        )
        return await self._to_public_works(selected)

    async def list_active(
        self,
        *,
        limit: int,
        offset: int,
    ) -> RecommendationWorkPage:
        if not 1 <= limit <= _MAX_PAGE_SIZE or offset < 0:
            raise ValueError("Invalid catalog recommendation pagination.")

        records = await self._list_records()
        active = tuple(
            record for record in records if record.active_passage_count > 0
        )
        page = active[offset : offset + limit]
        return RecommendationWorkPage(
            works=await self._to_public_works(page),
            total=len(active),
            limit=limit,
            offset=offset,
        )

    async def _list_records(self) -> tuple[WorkCatalogRecord, ...]:
        async with self._uow as uow:
            return tuple(await uow.work_repository.list_works())

    async def _to_public_works(
        self,
        records: tuple[WorkCatalogRecord, ...],
    ) -> tuple[RecommendationWork, ...]:
        cover_urls = await asyncio.gather(
            *(self._resolve_cover_url(record) for record in records)
        )
        return tuple(
            RecommendationWork(
                work_id=record.work.id.value,
                title=record.work.title,
                author_name=record.author.name,
                synopsis=record.work.synopsis,
                cover_image_url=cover_url,
                active_passage_count=record.active_passage_count,
                work_type=record.work.work_type,
                language=record.work.language,
                author_description=record.author.description,
            )
            for record, cover_url in zip(records, cover_urls, strict=True)
        )

    async def _resolve_cover_url(
        self,
        record: WorkCatalogRecord,
    ) -> str | None:
        if not record.work.cover_object_key:
            return record.work.cover_image_url
        try:
            return await self._cover_storage.create_read_url(
                object_key=record.work.cover_object_key
            )
        except WorkCoverStorageError:
            _LOGGER.warning(
                "Recommendation cover unavailable: work_id=%s",
                record.work.id.value,
            )
            return None

    @staticmethod
    def _validate_work_ids(work_ids: tuple[str, ...]) -> None:
        if len(work_ids) > _MAX_LOOKUP_SIZE:
            raise ValueError(
                f"At most {_MAX_LOOKUP_SIZE} works may be queried."
            )
        if len(work_ids) != len(set(work_ids)):
            raise ValueError("Work IDs must be unique.")
        if any(not work_id.strip() for work_id in work_ids):
            raise ValueError("Work IDs must not be empty.")
