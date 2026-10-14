from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self

from src.modules.catalog.domain.ports.repositories.ipassage_repository import (
    IPassageRepository,
)
from src.modules.catalog.domain.ports.repositories.itheme_repository import (
    IThemeRepository,
)
from src.modules.catalog.domain.ports.repositories.iwork_repository import (
    IWorkRepository,
)


class ICatalogGraphUnitOfWork(Protocol):
    @property
    def theme_repository(self) -> IThemeRepository: ...

    @property
    def work_repository(self) -> IWorkRepository: ...

    @property
    def passage_repository(self) -> IPassageRepository: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
