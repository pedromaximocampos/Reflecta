from typing import Protocol, TypeVar, Optional, Type
from types import TracebackType

from src.modules.journal.domain.ports.repositories.ijournal_entry_repository import IJournalEntryRepository

TJournalUow = TypeVar("TJournalUow", bound="IJournalUnitOfWork")



class IJournalUnitOfWork(Protocol):
    # repos
    @property
    def journal_entry_repository(self) -> IJournalEntryRepository: ...

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...


    # async context manager
    async def __aenter__(self: TJournalUow) -> TJournalUow: ...

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb: Optional[TracebackType],
    ) -> None: ...
