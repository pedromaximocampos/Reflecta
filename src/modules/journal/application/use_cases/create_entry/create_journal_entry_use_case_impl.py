from datetime import datetime

from src.domain.ports.system.iclock import IClock
from src.domain.ports.system.iulid_generator import IULIDGenerator
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.ports.units_of_work.ijournal_unit_of_work import IJournalUnitOfWork
from src.modules.journal.domain.value_objects.journal_entry_status import JournalEntryStatus

from .dto import CreateJournalEntryDTO
from .icreate_journal_entry_use_case import ICreateJournalEntryUseCase




class CreateJournalEntryUseCaseImpl(ICreateJournalEntryUseCase):


    def __init__(self, journal_unit_of_work: IJournalUnitOfWork, system_clock: IClock, ulid_generator: IULIDGenerator,) -> None:
        self.__journal_unit_of_work = journal_unit_of_work
        self.__system_clock = system_clock
        self.__ulid_generator = ulid_generator


    async def execute(self, create_journal_entry_dto: CreateJournalEntryDTO) -> None:
        now = self.__system_clock.now()
        async with self.__journal_unit_of_work as uow:
            journal_entry = self.__create_journal_entry_from_dto(create_journal_entry_dto, now)

            await uow.commit()


    def __create_journal_entry_from_dto(self, journal_entry_dto: CreateJournalEntryDTO, now: datetime) -> JournalEntry:
        ulid  = self.__ulid_generator.generate_ulid()
        return JournalEntry(
            id=ulid,
            user_id=journal_entry_dto.user_id,
            title=journal_entry_dto.title,
            content_text=journal_entry_dto.content_text,
            status=JournalEntryStatus.DRAFT,
            created_at=now,
        )
