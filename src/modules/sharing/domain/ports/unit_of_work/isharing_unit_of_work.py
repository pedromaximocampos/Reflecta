from types import TracebackType
from typing import Protocol, Self

from src.modules.internal_events.public import IOutboxRepository
from src.modules.sharing.domain.ports.repositories import (
    IProfessionalActivityRepository,
)


class ISharingUnitOfWork(Protocol):
    @property
    def activity_repository(self) -> IProfessionalActivityRepository: ...

    @property
    def outbox_repository(self) -> IOutboxRepository: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

