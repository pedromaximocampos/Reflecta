from src.modules.catalog.application.use_cases.create_work.dto import CreateWorkInputDTO
from src.modules.catalog.application.use_cases.create_work.icreate_work_use_case import ICreateWorkUseCase
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class CreateWorkController(IControllerInterface):
    def __init__(self, create_work_use_case: ICreateWorkUseCase) -> None:
        self.__create_work_use_case = create_work_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.body is None:
            raise ValueError("Request body cannot be None")
        work_input = CreateWorkInputDTO.from_dict(request.body)
        created_work = await self.__create_work_use_case.execute(work_input)
        return HttpResponse(status_code=201, body=created_work.to_dict())
