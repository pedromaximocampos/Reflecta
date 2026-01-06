from typing import Protocol, TypeVar, Optional, Type
from src.domain.ports.repositories.ijournal_entry_repository import IJournalEntryRepository
from src.domain.ports.units_of_work.iauth_unit_of_work import TAuthUow
from types import TracebackType

TJournalUow = TypeVar("TJournalUow", bound="IJournalUnitOfWork")



class IJournalUnitOfWork(Protocol):
    # repos
    @property
    def journal_entry_repository(self) -> IJournalEntryRepository: ...

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...


    # async context manager
    async def __aenter__(self: TAuthUow) -> TAuthUow: ...

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb: Optional[TracebackType],
    ) -> None: ...