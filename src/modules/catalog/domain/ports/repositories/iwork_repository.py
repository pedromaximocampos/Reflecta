from typing import Protocol

from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.public.work_id import WorkId


class IWorkRepository(Protocol):
    async def get_work_by_id(self, work_id: WorkId) -> Work | None: ...

    async def get_work_by_slug(self, slug: str) -> Work | None: ...

    async def create_work(self, work: Work, author: Author) -> tuple[Work, Author]: ...
