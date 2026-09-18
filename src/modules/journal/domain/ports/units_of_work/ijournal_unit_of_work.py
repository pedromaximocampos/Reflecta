from types import TracebackType
from typing import Protocol, TypeVar

from src.modules.journal.domain.ports.repositories.ijournal_entry_repository import (
    IJournalEntryRepository,
)

TJournalUow = TypeVar("TJournalUow", bound="IJournalUnitOfWork")


class IJournalUnitOfWork(Protocol):
    @property
    def journal_entry_repository(self) -> IJournalEntryRepository: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self: TJournalUow) -> TJournalUow: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
