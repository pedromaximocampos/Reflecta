from typing import Protocol

from src.domain.entities.journal_entry import JournalEntry


class IJournalEntryRepository(Protocol):

    async def create_journal_entry(self, journal_entry: JournalEntry) -> None: ...