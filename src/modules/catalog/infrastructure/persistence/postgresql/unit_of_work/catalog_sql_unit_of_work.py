from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.catalog.domain.entities.work_ingestion import WorkIngestion
from src.modules.catalog.domain.ports.repositories.iwork_ingestion_repository import (
    IWorkIngestionRepository,
)
from src.modules.catalog.domain.ports.unit_of_work.icatalog_sql_unit_of_work import (
    ICatalogSQLUnitOfWork,
)
from src.modules.catalog.infrastructure.persistence.postgresql.models.work_ingestion_model import (
    WorkIngestionModel,
)
from src.modules.catalog.infrastructure.persistence.postgresql.repositories.work_ingestion_repository import (
    WorkIngestionRepository,
)
from src.modules.internal_events.infrastructure.persistence.postgresql.models.outbox_model import (
    OutboxModel,
)
from src.modules.internal_events.infrastructure.persistence.postgresql.repositories.outbox_repository import (
    OutboxRepository,
)
from src.modules.internal_events.public import IOutboxRepository, OutboxEvent
from src.shared.domain.ports.system.iclock import IClock
from src.shared.infrastructure.persistence.mappers.interface import IMapper
from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler
from src.shared.infrastructure.persistence.postgresql.units_of_work.base_unit_of_work import (
    SQLAlchemyUnitOfWork,
)


class CatalogSQLUnitOfWork(SQLAlchemyUnitOfWork, ICatalogSQLUnitOfWork):
    def __init__(
        self,
        db: DBConnectionHandler,
        system_clock: IClock,
        work_ingestion_mapper: IMapper[WorkIngestionModel, WorkIngestion],
        outbox_mapper: IMapper[OutboxModel, OutboxEvent],
    ) -> None:
        super().__init__(db)
        self.__system_clock = system_clock
        self.__work_ingestion_mapper = work_ingestion_mapper
        self.__outbox_mapper = outbox_mapper
        self.__work_ingestion_repository: IWorkIngestionRepository | None = None
        self.__outbox_repository: IOutboxRepository | None = None

    @property
    def work_ingestion_repository(self) -> IWorkIngestionRepository:
        if self.__work_ingestion_repository is None:
            raise RuntimeError("Unit of work is not active.")
        return self.__work_ingestion_repository

    @property
    def outbox_repository(self) -> IOutboxRepository:
        if self.__outbox_repository is None:
            raise RuntimeError("Unit of work is not active.")
        return self.__outbox_repository

    async def _init_repositories(self, session: AsyncSession) -> None:
        self.__work_ingestion_repository = WorkIngestionRepository(
            session,
            self.__work_ingestion_mapper,
        )
        self.__outbox_repository = OutboxRepository(
            session,
            self.__outbox_mapper,
            self.__system_clock,
        )

    def _clear_repositories(self) -> None:
        self.__work_ingestion_repository = None
        self.__outbox_repository = None
