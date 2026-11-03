from src.modules.catalog.application.use_cases.update_work_cover import (
    IRemoveWorkCoverUseCase,
    IReplaceWorkCoverUseCase,
    RemoveWorkCoverInputDTO,
    ReplaceWorkCoverInputDTO,
)
from src.modules.catalog.public.work_id import WorkId
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class ReplaceWorkCoverController(IControllerInterface):
    def __init__(self, replace_work_cover_use_case: IReplaceWorkCoverUseCase) -> None:
        self.__replace_work_cover_use_case = replace_work_cover_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        payload = dict(request.body or {})
        work = await self.__replace_work_cover_use_case.execute(
            ReplaceWorkCoverInputDTO(
                work_id=WorkId(str(request.path_params["work_id"])),
                content=payload["content"],
                content_type=payload["content_type"],
                size_bytes=payload["size_bytes"],
            )
        )
        return HttpResponse(status_code=200, body=work.to_dict())


class RemoveWorkCoverController(IControllerInterface):
    def __init__(self, remove_work_cover_use_case: IRemoveWorkCoverUseCase) -> None:
        self.__remove_work_cover_use_case = remove_work_cover_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        work = await self.__remove_work_cover_use_case.execute(
            RemoveWorkCoverInputDTO(
                work_id=WorkId(str(request.path_params["work_id"])),
            )
        )
        return HttpResponse(status_code=200, body=work.to_dict())
