from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from src.modules.catalog.domain.entities.passage import Passage
from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(frozen=True, slots=True)
class ContextualPassageRecord:
    passage_id: str
    matched_theme_id: str
    matched_theme_confidence: float
    short_text: str
    paraphrase: str
    interpretation_note: str
    locator: str
    priority: int
    work_id: str
    work_title: str
    author_name: str
    start_page: int | None
    end_page: int | None


class IPassageRepository(Protocol):
    async def get_by_id(self, passage_id: PassageId) -> Passage | None: ...

    async def list_passages(
        self,
        *,
        status: CatalogStatus | None = None,
        work_id: WorkId | None = None,
        ingestion_id: WorkIngestionId | None = None,
    ) -> list[Passage]: ...

    async def find_active_contextual_candidates(
        self,
        *,
        theme_ids: tuple[str, ...],
        limit_per_theme: int,
    ) -> list[ContextualPassageRecord]: ...

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
