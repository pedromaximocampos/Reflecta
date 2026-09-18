from src.modules.journal.application.dto.journal_entry import JournalEntriesOutputDTO
from src.modules.journal.application.use_cases.list_entries.dto import (
    ListJournalEntriesInputDTO,
)
from src.modules.journal.application.use_cases.list_entries.ilist_journal_entries_use_case import (
    IListJournalEntriesUseCase,
)
from src.modules.journal.domain.ports.units_of_work.ijournal_unit_of_work import (
    IJournalUnitOfWork,
)


class ListJournalEntriesUseCase(IListJournalEntriesUseCase):
    def __init__(self, journal_unit_of_work: IJournalUnitOfWork) -> None:
        self.__journal_unit_of_work = journal_unit_of_work

    async def execute(
        self,
        journal_input: ListJournalEntriesInputDTO,
    ) -> JournalEntriesOutputDTO:
        async with self.__journal_unit_of_work as uow:
            entries = await uow.journal_entry_repository.list_by_user(
                journal_input.user_id,
                limit=journal_input.limit,
                offset=journal_input.offset,
            )
            return JournalEntriesOutputDTO.from_entities(entries)
