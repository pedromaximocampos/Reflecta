from typing import Protocol

from src.modules.journal.application.use_cases.delete_entry.dto import (
    DeleteJournalEntryInputDTO,
)


class IDeleteJournalEntryUseCase(Protocol):
    async def execute(self, journal_input: DeleteJournalEntryInputDTO) -> None: ...
