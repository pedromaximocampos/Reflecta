from src.modules.catalog.application.use_cases.get_works import (
    IGetAllWorksUseCase,
    IGetWorkByIdUseCase,
)
from src.modules.catalog.public.work_id import WorkId
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class GetWorkByIdController(IControllerInterface):
    def __init__(self, get_work_by_id_use_case: IGetWorkByIdUseCase) -> None:
        self.__get_work_by_id_use_case = get_work_by_id_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        work_id = WorkId(str(request.path_params["work_id"]))
        work = await self.__get_work_by_id_use_case.execute(work_id)
        return HttpResponse(status_code=200, body=work.to_dict())


class GetAllWorksController(IControllerInterface):
    def __init__(self, get_all_works_use_case: IGetAllWorksUseCase) -> None:
        self.__get_all_works_use_case = get_all_works_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        works = await self.__get_all_works_use_case.execute()
        return HttpResponse(status_code=200, body=works.to_dict())
