from src.modules.journal.application.dto.journal_entry import (
    JournalEntryOutputDTO,
    JournalEntryWindowOutputDTO,
)
from src.modules.journal.application.use_cases.list_entry_window.dto import (
    ListJournalEntryWindowInputDTO,
)
from src.modules.journal.domain.ports.units_of_work.ijournal_unit_of_work import (
    IJournalUnitOfWork,
)
from src.modules.journal.domain.exceptions.journal_exceptions import (
    InvalidJournalWindowError,
)


class ListJournalEntryWindowUseCase:
    def __init__(self, journal_unit_of_work: IJournalUnitOfWork) -> None:
        self.__journal_unit_of_work = journal_unit_of_work

    async def execute(
        self,
        journal_input: ListJournalEntryWindowInputDTO,
    ) -> JournalEntryWindowOutputDTO:
        if journal_input.center_date is not None:
            if (
                journal_input.end_date is not None
                or not 0 <= journal_input.before_days <= 31
                or not 0 <= journal_input.after_days <= 31
            ):
                raise InvalidJournalWindowError()
        async with self.__journal_unit_of_work as uow:
            window = await uow.journal_entry_repository.list_window_by_user(
                journal_input.user_id,
                end_date=journal_input.end_date,
                days=journal_input.days,
                center_date=journal_input.center_date,
                before_days=journal_input.before_days,
                after_days=journal_input.after_days,
            )
            return JournalEntryWindowOutputDTO(
                entries=tuple(
                    JournalEntryOutputDTO.from_entity(entry)
                    for entry in window.entries
                ),
                window_start=window.start_date,
                window_end=window.end_date,
                next_end_date=window.next_end_date,
            )
