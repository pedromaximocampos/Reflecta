from src.modules.catalog.application.use_cases.get_themes.iget_all_themes_use_case import (
    IGetAllThemesUseCase,
)
from src.modules.catalog.application.use_cases.get_themes.iget_theme_by_id_use_case import (
    IGetThemeByIdUseCase,
)
from src.modules.catalog.public.theme_id import ThemeId
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class GetThemeByIdController(IControllerInterface):
    def __init__(self, get_theme_by_id_use_case: IGetThemeByIdUseCase) -> None:
        self.__get_theme_by_id_use_case = get_theme_by_id_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        theme_id = ThemeId(str(request.path_params["theme_id"]))
        theme = await self.__get_theme_by_id_use_case.execute(theme_id)
        return HttpResponse(status_code=200, body=theme.to_dict())


class GetAllThemesController(IControllerInterface):
    def __init__(self, get_all_themes_use_case: IGetAllThemesUseCase) -> None:
        self.__get_all_themes_use_case = get_all_themes_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        themes = await self.__get_all_themes_use_case.execute()
        return HttpResponse(status_code=200, body=themes.to_dict())
