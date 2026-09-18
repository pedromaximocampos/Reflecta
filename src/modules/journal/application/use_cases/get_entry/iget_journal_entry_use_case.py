from typing import Protocol

from src.modules.journal.application.dto.journal_entry import JournalEntryOutputDTO
from src.modules.journal.application.use_cases.get_entry.dto import (
    GetJournalEntryInputDTO,
)


class IGetJournalEntryUseCase(Protocol):
    async def execute(
        self,
        journal_input: GetJournalEntryInputDTO,
    ) -> JournalEntryOutputDTO: ...
