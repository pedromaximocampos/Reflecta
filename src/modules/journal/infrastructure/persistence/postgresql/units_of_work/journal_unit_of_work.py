from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.ports.repositories.ijournal_entry_repository import (
    IJournalEntryRepository,
)
from src.modules.journal.domain.ports.units_of_work.ijournal_unit_of_work import (
    IJournalUnitOfWork,
)
from src.modules.journal.infrastructure.persistence.postgresql.mappers.journal_entry_mapper import (
    JournalEntryMapper,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import (
    JournalEntryModel,
)
from src.modules.journal.infrastructure.persistence.postgresql.repositories.journal_entry_repository import (
    JournalEntryRepository,
)
from src.shared.infrastructure.persistence.mappers.interface import IMapper
from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler
from src.shared.infrastructure.persistence.postgresql.units_of_work.base_unit_of_work import (
    SQLAlchemyUnitOfWork,
)


class JournalUnitOfWork(SQLAlchemyUnitOfWork, IJournalUnitOfWork):
    def __init__(
        self,
        db: DBConnectionHandler,
        journal_entry_mapper: IMapper[JournalEntryModel, JournalEntry] | None = None,
    ) -> None:
        super().__init__(db)
        self.__journal_entry_mapper = journal_entry_mapper or JournalEntryMapper()
        self.__journal_entry_repository: IJournalEntryRepository | None = None

    @property
    def journal_entry_repository(self) -> IJournalEntryRepository:
        if self.__journal_entry_repository is None:
            raise RuntimeError("Unit of work is not active.")
        return self.__journal_entry_repository

    async def _init_repositories(self, session: AsyncSession) -> None:
        self.__journal_entry_repository = JournalEntryRepository(
            session,
            self.__journal_entry_mapper,
        )

    def _clear_repositories(self) -> None:
        self.__journal_entry_repository = None
