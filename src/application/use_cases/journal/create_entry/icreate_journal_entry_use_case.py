from typing import Protocol

from src.application.use_cases.journal.create_entry.dto import CreateJournalEntryDTO


class ICreateJournalEntryUseCase(Protocol):


    async def execute(self, create_journal_entry_dto: CreateJournalEntryDTO) -> None: ...