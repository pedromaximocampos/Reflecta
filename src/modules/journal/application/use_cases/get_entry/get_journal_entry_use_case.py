from src.modules.journal.application.dto.journal_entry import JournalEntryOutputDTO
from src.modules.journal.application.use_cases.get_entry.dto import (
    GetJournalEntryInputDTO,
)
from src.modules.journal.application.use_cases.get_entry.iget_journal_entry_use_case import (
    IGetJournalEntryUseCase,
)
from src.modules.journal.domain.exceptions.journal_exceptions import (
    JournalEntryNotFoundError,
)
from src.modules.journal.domain.ports.units_of_work.ijournal_unit_of_work import (
    IJournalUnitOfWork,
)


class GetJournalEntryUseCase(IGetJournalEntryUseCase):
    def __init__(self, journal_unit_of_work: IJournalUnitOfWork) -> None:
        self.__journal_unit_of_work = journal_unit_of_work

    async def execute(
        self,
        journal_input: GetJournalEntryInputDTO,
    ) -> JournalEntryOutputDTO:
        async with self.__journal_unit_of_work as uow:
            entry = await uow.journal_entry_repository.find_by_id_for_user(
                journal_input.journal_entry_id,
                journal_input.user_id,
            )
            if entry is None:
                raise JournalEntryNotFoundError()

            return JournalEntryOutputDTO.from_entity(entry)
