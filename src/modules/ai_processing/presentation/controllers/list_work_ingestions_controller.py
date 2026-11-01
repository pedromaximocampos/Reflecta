from src.modules.ai_processing.application.use_cases.list_work_ingestions import (
    IListWorkIngestionsUseCase,
)
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class ListWorkIngestionsController(IControllerInterface):
    def __init__(self, use_case: IListWorkIngestionsUseCase) -> None:
        self._use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        limit = int(request.query_params.get("limit", "50"))
        result = await self._use_case.execute(limit=limit)
        return HttpResponse(status_code=200, body=result.to_dict())
