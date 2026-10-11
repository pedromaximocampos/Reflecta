from collections.abc import Sequence
from typing import Protocol

from src.modules.catalog.domain.entities.passage import Passage
from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


class IPassageRepository(Protocol):
    async def get_by_id(self, passage_id: PassageId) -> Passage | None: ...

    async def list_passages(
        self,
        *,
        status: CatalogStatus | None = None,
        work_id: WorkId | None = None,
        ingestion_id: WorkIngestionId | None = None,
    ) -> list[Passage]: ...

    async def create(self, passage: Passage) -> Passage: ...

    async def update(self, passage: Passage) -> Passage: ...

    async def count_pending_by_ingestion(
        self,
        ingestion_id: WorkIngestionId,
    ) -> int: ...

    async def replace_ai_candidates_for_chunk(
        self,
        *,
        ingestion_id: WorkIngestionId,
        work_id: WorkId,
        chunk_id: str,
        passages: Sequence[Passage],
    ) -> None: ...
