from __future__ import annotations

from types import TracebackType
from typing import Protocol, TypeVar

from src.modules.catalog.domain.ports.repositories.iwork_ingestion_repository import (
    IWorkIngestionRepository,
)
from src.modules.internal_events.public import IOutboxRepository


TCatalogSqlUow = TypeVar("TCatalogSqlUow", bound="ICatalogSQLUnitOfWork")


class ICatalogSQLUnitOfWork(Protocol):
    @property
    def work_ingestion_repository(self) -> IWorkIngestionRepository: ...

    @property
    def outbox_repository(self) -> IOutboxRepository: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self: TCatalogSqlUow) -> TCatalogSqlUow: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
