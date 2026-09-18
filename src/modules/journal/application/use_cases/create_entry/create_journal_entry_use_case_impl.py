from src.modules.journal.application.dto.journal_entry import JournalEntryOutputDTO
from src.modules.journal.application.use_cases.create_entry.dto import (
    CreateJournalEntryDTO,
)
from src.modules.journal.application.use_cases.create_entry.icreate_journal_entry_use_case import (
    ICreateJournalEntryUseCase,
)
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.ports.units_of_work.ijournal_unit_of_work import (
    IJournalUnitOfWork,
)
from src.modules.journal.domain.value_objects.journal_entry_status import (
    JournalEntryStatus,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


class CreateJournalEntryUseCaseImpl(ICreateJournalEntryUseCase):
    def __init__(
        self,
        journal_unit_of_work: IJournalUnitOfWork,
        system_clock: IClock,
        ulid_generator: IULIDGenerator,
    ) -> None:
        self.__journal_unit_of_work = journal_unit_of_work
        self.__system_clock = system_clock
        self.__ulid_generator = ulid_generator

    async def execute(
        self,
        create_journal_entry_dto: CreateJournalEntryDTO,
    ) -> JournalEntryOutputDTO:
        journal_entry = JournalEntry(
            id=JournalEntryId(self.__ulid_generator.generate_ulid()),
            user_id=create_journal_entry_dto.user_id,
            title=create_journal_entry_dto.title,
            content_text=create_journal_entry_dto.content_text,
            context_tags=create_journal_entry_dto.context_tags,
            status=JournalEntryStatus.DRAFT,
            created_at=self.__system_clock.now(),
        )

        async with self.__journal_unit_of_work as uow:
            created_entry = await uow.journal_entry_repository.create(journal_entry)
            output = JournalEntryOutputDTO.from_entity(created_entry)
            await uow.commit()

        return output
