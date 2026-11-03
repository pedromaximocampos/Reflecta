from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.public.work_id import WorkId


@dataclass(frozen=True, slots=True)
class WorkCatalogRecord:
    work: Work
    author: Author
    passage_count: int
    active_passage_count: int
    inactive_passage_count: int


class IWorkRepository(Protocol):
    async def get_work_by_id(self, work_id: WorkId) -> Work | None: ...

    async def get_work_with_author_by_id(
        self,
        work_id: WorkId,
    ) -> WorkCatalogRecord | None: ...

    async def get_work_by_slug(self, slug: str) -> Work | None: ...

    async def list_works(self) -> list[WorkCatalogRecord]: ...

    async def update_work(self, work: Work) -> Work: ...

    async def sync_status_from_active_passages(
        self,
        work_id: WorkId,
        updated_at: datetime,
    ) -> Work: ...

    async def create_work(self, work: Work, author: Author) -> tuple[Work, Author]: ...
