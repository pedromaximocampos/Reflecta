from src.modules.catalog.application.use_cases.delete_themes.idelete_theme_by_id_use_case import (
    IDeleteThemeByIdUseCase,
)
from src.modules.catalog.public.theme_id import ThemeId
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class DeleteThemeByIdController(IControllerInterface):
    def __init__(self, delete_theme_by_id_use_case: IDeleteThemeByIdUseCase) -> None:
        self.__delete_theme_by_id_use_case = delete_theme_by_id_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        theme_id = ThemeId(str(request.path_params["theme_id"]))
        await self.__delete_theme_by_id_use_case.execute(theme_id)
        return HttpResponse(status_code=204)
