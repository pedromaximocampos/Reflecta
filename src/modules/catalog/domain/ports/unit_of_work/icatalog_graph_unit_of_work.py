from __future__ import annotations

from types import TracebackType
from typing import Protocol, TypeVar

from src.modules.catalog.domain.ports.repositories.itheme_repository import IThemeRepository


TCatalogUow = TypeVar("TCatalogUow", bound="ICatalogGraphUnitOfWork")


class ICatalogGraphUnitOfWork(Protocol):
    @property
    def theme_repository(self) -> IThemeRepository: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self: TCatalogUow) -> TCatalogUow: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
