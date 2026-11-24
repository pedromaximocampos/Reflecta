from src.modules.journal.application.use_cases.list_entry_calendar.dto import (
    JournalEntryCalendarItemOutputDTO,
    JournalEntryCalendarOutputDTO,
    ListJournalEntryCalendarInputDTO,
)
from src.modules.journal.domain.exceptions.journal_exceptions import (
    InvalidJournalCalendarRangeError,
)
from src.modules.journal.domain.ports.units_of_work.ijournal_unit_of_work import (
    IJournalUnitOfWork,
)


class ListJournalEntryCalendarUseCase:
    def __init__(self, journal_unit_of_work: IJournalUnitOfWork) -> None:
        self.__journal_unit_of_work = journal_unit_of_work

    async def execute(
        self,
        journal_input: ListJournalEntryCalendarInputDTO,
    ) -> JournalEntryCalendarOutputDTO:
        range_days = (journal_input.end_date - journal_input.start_date).days + 1
        if not 1 <= range_days <= 366:
            raise InvalidJournalCalendarRangeError()

        async with self.__journal_unit_of_work as uow:
            entries = await uow.journal_entry_repository.list_calendar_by_user(
                journal_input.user_id,
                start_date=journal_input.start_date,
                end_date=journal_input.end_date,
            )
            return JournalEntryCalendarOutputDTO(
                entries=tuple(
                    JournalEntryCalendarItemOutputDTO(
                        id=entry.id.value,
                        entry_date=entry.entry_date,
                        status=entry.status,
                    )
                    for entry in entries
                ),
                start_date=journal_input.start_date,
                end_date=journal_input.end_date,
            )
