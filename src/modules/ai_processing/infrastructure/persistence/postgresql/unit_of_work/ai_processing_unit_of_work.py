from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ai_processing.domain.entities import InboxEvent, WorkIngestionChunk
from src.modules.ai_processing.domain.ports.repositories import (
    IInboxEventRepository,
    IWorkIngestionChunkRepository,
)
from src.modules.ai_processing.domain.ports.unit_of_work import (
    IAIProcessingUnitOfWork,
)
from src.modules.ai_processing.infrastructure.persistence.postgresql.models import (
    InboxEventModel,
    WorkIngestionChunkModel,
)
from src.modules.ai_processing.infrastructure.persistence.postgresql.repositories import (
    InboxEventRepository,
    WorkIngestionChunkRepository,
)
from src.shared.infrastructure.persistence.mappers.interface import IMapper
from src.shared.infrastructure.persistence.postgresql.connection import (
    DBConnectionHandler,
)
from src.shared.infrastructure.persistence.postgresql.units_of_work.base_unit_of_work import (
    SQLAlchemyUnitOfWork,
)


class AIProcessingUnitOfWork(SQLAlchemyUnitOfWork, IAIProcessingUnitOfWork):
    def __init__(
        self,
        db: DBConnectionHandler,
        work_ingestion_chunk_mapper: IMapper[
            WorkIngestionChunkModel,
            WorkIngestionChunk,
        ],
        inbox_event_mapper: IMapper[InboxEventModel, InboxEvent],
    ) -> None:
        super().__init__(db)
        self.__work_ingestion_chunk_mapper = work_ingestion_chunk_mapper
        self.__inbox_event_mapper = inbox_event_mapper
        self.__work_ingestion_chunk_repository: IWorkIngestionChunkRepository | None = (
            None
        )
        self.__inbox_event_repository: IInboxEventRepository | None = None

    @property
    def inbox_event_repository(self) -> IInboxEventRepository:
        if self.__inbox_event_repository is None:
            raise RuntimeError("Unit of work is not active.")
        return self.__inbox_event_repository

    @property
    def work_ingestion_chunk_repository(
        self,
    ) -> IWorkIngestionChunkRepository:
        if self.__work_ingestion_chunk_repository is None:
            raise RuntimeError("Unit of work is not active.")
        return self.__work_ingestion_chunk_repository

    async def _init_repositories(self, session: AsyncSession) -> None:
        self.__inbox_event_repository = InboxEventRepository(
            session,
            self.__inbox_event_mapper,
        )
        self.__work_ingestion_chunk_repository = WorkIngestionChunkRepository(
            session,
            self.__work_ingestion_chunk_mapper,
        )

    def _clear_repositories(self) -> None:
        self.__inbox_event_repository = None
        self.__work_ingestion_chunk_repository = None
