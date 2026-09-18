from typing import Protocol

from src.modules.journal.application.dto.journal_entry import JournalEntriesOutputDTO
from src.modules.journal.application.use_cases.list_entries.dto import (
    ListJournalEntriesInputDTO,
)


class IListJournalEntriesUseCase(Protocol):
    async def execute(
        self,
        journal_input: ListJournalEntriesInputDTO,
    ) -> JournalEntriesOutputDTO: ...
