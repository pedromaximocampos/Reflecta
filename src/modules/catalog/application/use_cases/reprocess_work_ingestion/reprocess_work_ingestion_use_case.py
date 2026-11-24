from src.modules.catalog.domain.events.work_ingestion_requested import (
    WorkIngestionRequested,
)
from src.modules.catalog.domain.exceptions.work_exceptions import (
    WorkIngestionNotFoundError,
    WorkIngestionNotReprocessableError,
)
from src.modules.catalog.domain.ports.unit_of_work import ICatalogSQLUnitOfWork
from src.modules.catalog.domain.value_objects import WorkIngestionStatus
from src.modules.internal_events.public import IOutboxService
from src.shared.domain.ports.system.iclock import IClock

from .dto import (
    ReprocessWorkIngestionInputDTO,
    ReprocessWorkIngestionOutputDTO,
)
from .ireprocess_work_ingestion_use_case import IReprocessWorkIngestionUseCase


class ReprocessWorkIngestionUseCase(IReprocessWorkIngestionUseCase):
    def __init__(
        self,
        catalog_sql_uow: ICatalogSQLUnitOfWork,
        outbox_service: IOutboxService,
        clock: IClock,
    ) -> None:
        self._catalog_sql_uow = catalog_sql_uow
        self._outbox_service = outbox_service
        self._clock = clock

    async def execute(
        self,
        ingestion_input: ReprocessWorkIngestionInputDTO,
    ) -> ReprocessWorkIngestionOutputDTO:
        async with self._catalog_sql_uow as uow:
            ingestion = await uow.work_ingestion_repository.find_by_id_for_update(
                ingestion_input.ingestion_id
            )
            if ingestion is None:
                raise WorkIngestionNotFoundError(
                    ingestion_input.ingestion_id.value
                )

            if ingestion.status in {
                WorkIngestionStatus.PENDING,
                WorkIngestionStatus.PROCESSING,
            }:
                return ReprocessWorkIngestionOutputDTO.from_entity(
                    ingestion,
                    event_created=False,
                )
            if ingestion.status is not WorkIngestionStatus.FAILED:
                raise WorkIngestionNotReprocessableError(
                    ingestion.id.value,
                    ingestion.status.value,
                )

            ingestion.request_reprocessing()
            updated = await uow.work_ingestion_repository.update(ingestion)
            event = WorkIngestionRequested(
                ingestion_id=updated.id,
                work_id=updated.work_id,
                requested_by=updated.requested_by,
                document_location=updated.document_location,
                occurred_at=self._clock.now(),
            )
            await self._outbox_service.persist_event(
                event,
                uow.outbox_repository,
            )
            await uow.commit()
            return ReprocessWorkIngestionOutputDTO.from_entity(
                updated,
                event_created=True,
            )
