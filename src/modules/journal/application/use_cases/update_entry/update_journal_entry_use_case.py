from src.modules.journal.application.dto.journal_entry import JournalEntryOutputDTO
from src.modules.journal.application.use_cases.update_entry.dto import (
    UpdateJournalEntryInputDTO,
)
from src.modules.journal.application.use_cases.update_entry.iupdate_journal_entry_use_case import (
    IUpdateJournalEntryUseCase,
)
from src.modules.journal.domain.exceptions.journal_exceptions import (
    EmptyJournalContentError,
    EmptyJournalUpdateError,
    JournalEntryNotFoundError,
)
from src.modules.journal.domain.ports.units_of_work.ijournal_unit_of_work import (
    IJournalUnitOfWork,
)
from src.shared.domain.ports.system.iclock import IClock


class UpdateJournalEntryUseCase(IUpdateJournalEntryUseCase):
    _ALLOWED_FIELDS = frozenset({"title", "content_text", "context_tags"})

    def __init__(
        self,
        journal_unit_of_work: IJournalUnitOfWork,
        system_clock: IClock,
    ) -> None:
        self.__journal_unit_of_work = journal_unit_of_work
        self.__system_clock = system_clock

    async def execute(
        self,
        journal_input: UpdateJournalEntryInputDTO,
    ) -> JournalEntryOutputDTO:
        if not journal_input.fields_to_update:
            raise EmptyJournalUpdateError()
        if not journal_input.fields_to_update.issubset(self._ALLOWED_FIELDS):
            raise ValueError("Invalid journal fields for update.")

        async with self.__journal_unit_of_work as uow:
            entry = await uow.journal_entry_repository.find_by_id_for_user(
                journal_input.journal_entry_id,
                journal_input.user_id,
            )
            if entry is None:
                raise JournalEntryNotFoundError()

            now = self.__system_clock.now()
            if "title" in journal_input.fields_to_update:
                entry.update_title(journal_input.title, now=now)
            if "content_text" in journal_input.fields_to_update:
                if journal_input.content_text is None:
                    raise EmptyJournalContentError()
                entry.update_content(journal_input.content_text, now=now)
            if "context_tags" in journal_input.fields_to_update:
                entry.update_context_tags(journal_input.context_tags, now=now)

            updated_entry = await uow.journal_entry_repository.update(
                entry,
                journal_input.fields_to_update,
            )
            output = JournalEntryOutputDTO.from_entity(updated_entry)
            await uow.commit()

        return output
