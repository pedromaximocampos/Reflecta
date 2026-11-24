from src.modules.catalog.application.use_cases.reprocess_work_ingestion import (
    IReprocessWorkIngestionUseCase,
    ReprocessWorkIngestionInputDTO,
)
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class ReprocessWorkIngestionController(IControllerInterface):
    def __init__(
        self,
        reprocess_work_ingestion_use_case: IReprocessWorkIngestionUseCase,
    ) -> None:
        self._reprocess_work_ingestion_use_case = reprocess_work_ingestion_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        ingestion_id = request.path_params.get("ingestion_id")
        if ingestion_id is None:
            raise ValueError("Work ingestion ID cannot be None")

        output = await self._reprocess_work_ingestion_use_case.execute(
            ReprocessWorkIngestionInputDTO(
                ingestion_id=WorkIngestionId(ingestion_id),
            )
        )
        return HttpResponse(status_code=202, body=output.to_dict())
