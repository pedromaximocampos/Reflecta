from src.modules.catalog.application.use_cases.get_work_document_access import (
    GetWorkDocumentAccessInputDTO,
    IGetWorkDocumentAccessUseCase,
)
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class GetWorkDocumentAccessController(IControllerInterface):
    def __init__(self, use_case: IGetWorkDocumentAccessUseCase) -> None:
        self._use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        ingestion_id = request.path_params.get("ingestion_id")
        if ingestion_id is None:
            raise ValueError("Work ingestion ID cannot be None")
        output = await self._use_case.execute(
            GetWorkDocumentAccessInputDTO(
                ingestion_id=WorkIngestionId(ingestion_id),
            )
        )
        return HttpResponse(status_code=200, body=output.to_dict())
