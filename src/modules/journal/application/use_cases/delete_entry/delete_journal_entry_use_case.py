from src.modules.journal.application.use_cases.delete_entry.dto import (
    DeleteJournalEntryInputDTO,
)
from src.modules.journal.application.use_cases.delete_entry.idelete_journal_entry_use_case import (
    IDeleteJournalEntryUseCase,
)
from src.modules.journal.domain.exceptions.journal_exceptions import (
    JournalEntryNotFoundError,
)
from src.modules.journal.domain.ports.units_of_work.ijournal_unit_of_work import (
    IJournalUnitOfWork,
)
from src.shared.domain.ports.system.iclock import IClock


class DeleteJournalEntryUseCase(IDeleteJournalEntryUseCase):
    def __init__(
        self,
        journal_unit_of_work: IJournalUnitOfWork,
        system_clock: IClock,
    ) -> None:
        self.__journal_unit_of_work = journal_unit_of_work
        self.__system_clock = system_clock

    async def execute(self, journal_input: DeleteJournalEntryInputDTO) -> None:
        async with self.__journal_unit_of_work as uow:
            entry = await uow.journal_entry_repository.find_by_id_for_user(
                journal_input.journal_entry_id,
                journal_input.user_id,
            )
            if entry is None:
                raise JournalEntryNotFoundError()

            entry.delete(now=self.__system_clock.now())
            await uow.journal_entry_repository.soft_delete(entry)
            await uow.commit()
