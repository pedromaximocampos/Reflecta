from typing import Protocol

from src.modules.journal.application.dto.journal_entry import JournalEntryOutputDTO
from src.modules.journal.application.use_cases.update_entry.dto import (
    UpdateJournalEntryInputDTO,
)


class IUpdateJournalEntryUseCase(Protocol):
    async def execute(
        self,
        journal_input: UpdateJournalEntryInputDTO,
    ) -> JournalEntryOutputDTO: ...
