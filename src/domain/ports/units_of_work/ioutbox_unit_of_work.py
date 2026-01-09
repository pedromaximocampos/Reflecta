from types import TracebackType
from typing import Protocol, TypeVar, Optional, Type

from src.domain.ports.repositories.ioutbox_repository import IOutboxRepository

TOutboxUnitOfWork = TypeVar("TOutboxUnitOfWork", bound="IOutboxUnitOfWork")

class IOutboxUnitOfWork(Protocol):
    @property
    def outbox_repository(self) -> IOutboxRepository: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    # async context manager
    async def __aenter__(self: TOutboxUnitOfWork) -> TOutboxUnitOfWork: ...

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb: Optional[TracebackType],
    ) -> None: ...