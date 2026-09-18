from typing import Protocol

from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.public.journal_entry_id import JournalEntryId


class IJournalEntryRepository(Protocol):
    async def create(self, journal_entry: JournalEntry) -> JournalEntry: ...

    async def find_by_id_for_user(
        self,
        journal_entry_id: JournalEntryId,
        user_id: UserId,
    ) -> JournalEntry | None: ...

    async def list_by_user(
        self,
        user_id: UserId,
        *,
        limit: int,
        offset: int,
    ) -> list[JournalEntry]: ...

    async def update(
        self,
        journal_entry: JournalEntry,
        fields_to_update: frozenset[str],
    ) -> JournalEntry: ...

    async def soft_delete(self, journal_entry: JournalEntry) -> None: ...
