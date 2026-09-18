from typing import Protocol

from .dto import CreateJournalEntryDTO, CreateJournalEntryOutputDTO

class ICreateJournalEntryUseCase(Protocol):
    async def execute(
        self,
        create_journal_entry_dto: CreateJournalEntryDTO,
    ) -> CreateJournalEntryOutputDTO: ...
