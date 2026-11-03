from src.modules.ai_processing.application.ports.catalog import (
    IWorkIngestionQueryCatalog,
)
from src.modules.ai_processing.application.ports.operations import (
    IWorkIngestionFailureQuery,
)
from src.modules.ai_processing.domain.ports.unit_of_work import (
    IAIProcessingUnitOfWork,
)

from .dto import (
    WorkIngestionFailureOutputDTO,
    WorkIngestionOutputDTO,
    WorkIngestionProgressOutputDTO,
    WorkIngestionsOutputDTO,
)
from .ilist_work_ingestions_use_case import IListWorkIngestionsUseCase


class ListWorkIngestionsUseCase(IListWorkIngestionsUseCase):
    def __init__(
        self,
        catalog: IWorkIngestionQueryCatalog,
        ai_processing_uow: IAIProcessingUnitOfWork,
        failure_query: IWorkIngestionFailureQuery,
    ) -> None:
        self._catalog = catalog
        self._ai_processing_uow = ai_processing_uow
        self._failure_query = failure_query

    async def execute(self, *, limit: int) -> WorkIngestionsOutputDTO:
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        summaries = await self._catalog.list_recent(limit=limit)
        ingestion_ids = tuple(item.ingestion_id for item in summaries)
        async with self._ai_processing_uow as uow:
            counts_by_ingestion = (
                await uow.work_ingestion_chunk_repository.count_many_by_status(
                    ingestion_ids
                )
            )
        failures_by_ingestion = (
            await self._failure_query.latest_active_for_ingestions(ingestion_ids)
        )
        return WorkIngestionsOutputDTO(
            tuple(
                WorkIngestionOutputDTO.from_summary(
                    summary,
                    WorkIngestionProgressOutputDTO.from_counts(
                        counts_by_ingestion.get(summary.ingestion_id, {})
                    ),
                    WorkIngestionFailureOutputDTO.from_record(
                        failures_by_ingestion.get(summary.ingestion_id.value)
                    ),
                )
                for summary in summaries
            )
        )
