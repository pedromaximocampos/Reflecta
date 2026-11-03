from sqlalchemy import case, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.catalog.domain.entities.work_ingestion import WorkIngestion
from src.modules.catalog.domain.ports.repositories.iwork_ingestion_repository import (
    IWorkIngestionRepository,
)
from src.modules.catalog.infrastructure.persistence.postgresql.models.work_ingestion_model import (
    WorkIngestionModel,
)
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.modules.catalog.domain.value_objects.work_ingestion_status import (
    WorkIngestionStatus,
)
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class WorkIngestionRepository(IWorkIngestionRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: IMapper[WorkIngestionModel, WorkIngestion],
    ) -> None:
        self.__session = session
        self.__mapper = mapper

    async def create(self, ingestion: WorkIngestion) -> WorkIngestion:
        model = self.__mapper.to_model(ingestion)
        self.__session.add(model)
        await self.__session.flush()
        return self.__mapper.to_entity(model)

    async def find_by_id(
        self,
        ingestion_id: WorkIngestionId,
    ) -> WorkIngestion | None:
        query = select(WorkIngestionModel).where(
            WorkIngestionModel.id == ingestion_id.value,
        )
        result = await self.__session.execute(query)
        model = result.scalar_one_or_none()
        return self.__mapper.to_entity(model) if model is not None else None

    async def list_recent(self, *, limit: int) -> tuple[WorkIngestion, ...]:
        status_priority = case(
            (WorkIngestionModel.status == WorkIngestionStatus.PROCESSING.value, 0),
            (WorkIngestionModel.status == WorkIngestionStatus.PENDING.value, 1),
            (WorkIngestionModel.status == WorkIngestionStatus.FAILED.value, 2),
            (
                WorkIngestionModel.status
                == WorkIngestionStatus.PENDING_REVIEW.value,
                3,
            ),
            (WorkIngestionModel.status == WorkIngestionStatus.COMPLETED.value, 4),
            else_=5,
        )
        query = (
            select(WorkIngestionModel)
            .order_by(
                status_priority,
                WorkIngestionModel.created_at.desc(),
                WorkIngestionModel.id.desc(),
            )
            .limit(limit)
        )
        result = await self.__session.execute(query)
        return tuple(self.__mapper.to_entity(model) for model in result.scalars())

    async def update(self, ingestion: WorkIngestion) -> WorkIngestion:
        query = (
            update(WorkIngestionModel)
            .where(WorkIngestionModel.id == ingestion.id.value)
            .values(
                status=ingestion.status.value,
                attempts=ingestion.attempts,
                started_at=ingestion.started_at,
                finished_at=ingestion.finished_at,
                error_code=ingestion.error_code,
                error_message=ingestion.error_message,
            )
            .returning(WorkIngestionModel)
        )
        result = await self.__session.execute(query)
        model = result.scalar_one_or_none()
        if model is None:
            raise LookupError(
                f"Work ingestion '{ingestion.id.value}' was not found."
            )
        return self.__mapper.to_entity(model)
