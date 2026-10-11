from src.modules.auth.public import UserId
from src.modules.catalog.application.use_cases.request_work_ingestion import (
    IRequestWorkIngestionUseCase,
    RequestWorkIngestionInputDTO,
)
from src.modules.catalog.public.work_id import WorkId
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class RequestWorkIngestionController(IControllerInterface):
    def __init__(
        self,
        request_work_ingestion_use_case: IRequestWorkIngestionUseCase,
    ) -> None:
        self.__request_work_ingestion_use_case = request_work_ingestion_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.body is None:
            raise ValueError("Request body cannot be None")
        if request.authenticated_user_id is None:
            raise ValueError("Authenticated user ID cannot be None")

        work_id = request.path_params.get("work_id")
        if work_id is None:
            raise ValueError("Work ID cannot be None")

        ingestion_input = RequestWorkIngestionInputDTO(
            work_id=WorkId(work_id),
            requested_by=UserId(request.authenticated_user_id),
            filename=request.body["filename"],
            content_type=request.body["content_type"],
            size_bytes=request.body["size_bytes"],
            content=request.body["content"],
        )
        requested_ingestion = await self.__request_work_ingestion_use_case.execute(
            ingestion_input
        )
        return HttpResponse(status_code=202, body=requested_ingestion.to_dict())
