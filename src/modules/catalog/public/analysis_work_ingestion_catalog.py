from datetime import datetime

from src.modules.catalog.domain.ports.unit_of_work import ICatalogSQLUnitOfWork
from src.modules.catalog.domain.value_objects import WorkIngestionStatus
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


class AnalysisWorkIngestionCatalog:
    """Public Catalog boundary used by AI Processing to move the job lifecycle."""

    def __init__(self, uow: ICatalogSQLUnitOfWork) -> None:
        self._uow = uow

    async def mark_processing(
        self,
        ingestion_id: WorkIngestionId,
        *,
        now: datetime,
    ) -> bool:
        async with self._uow as uow:
            ingestion = await uow.work_ingestion_repository.find_by_id(ingestion_id)
            if ingestion is None:
                raise LookupError(
                    f"Work ingestion '{ingestion_id.value}' was not found."
                )
            if ingestion.status in {
                WorkIngestionStatus.PENDING_REVIEW,
                WorkIngestionStatus.COMPLETED,
            }:
                return False
            if ingestion.status is WorkIngestionStatus.PROCESSING:
                return True
            ingestion.mark_processing(now=now)
            await uow.work_ingestion_repository.update(ingestion)
            await uow.commit()
            return True

    async def mark_pending_review(
        self,
        ingestion_id: WorkIngestionId,
        *,
        now: datetime,
    ) -> None:
        async with self._uow as uow:
            ingestion = await uow.work_ingestion_repository.find_by_id(ingestion_id)
            if ingestion is None:
                raise LookupError(
                    f"Work ingestion '{ingestion_id.value}' was not found."
                )
            if ingestion.status in {
                WorkIngestionStatus.PENDING_REVIEW,
                WorkIngestionStatus.COMPLETED,
            }:
                return
            ingestion.mark_pending_review(now=now)
            await uow.work_ingestion_repository.update(ingestion)
            await uow.commit()

    async def mark_failed(
        self,
        ingestion_id: WorkIngestionId,
        *,
        now: datetime,
        error_code: str,
        error_message: str,
    ) -> None:
        async with self._uow as uow:
            ingestion = await uow.work_ingestion_repository.find_by_id(ingestion_id)
            if ingestion is None:
                raise LookupError(
                    f"Work ingestion '{ingestion_id.value}' was not found."
                )
            if ingestion.status is not WorkIngestionStatus.PROCESSING:
                return
            ingestion.mark_failed(
                now=now,
                error_code=error_code,
                error_message=error_message,
            )
            await uow.work_ingestion_repository.update(ingestion)
            await uow.commit()
