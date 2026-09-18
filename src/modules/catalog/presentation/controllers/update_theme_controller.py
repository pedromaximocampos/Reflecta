from src.modules.catalog.application.use_cases.update_themes.dto import (
    UpdateThemeInputDTO,
)
from src.modules.catalog.application.use_cases.update_themes.iupdate_theme_use_case import (
    IUpdateThemeUseCase,
)
from src.modules.catalog.public.theme_id import ThemeId
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class UpdateThemeController(IControllerInterface):
    def __init__(self, update_theme_use_case: IUpdateThemeUseCase) -> None:
        self.__update_theme_use_case = update_theme_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        payload = dict(request.body or {})
        theme_input = UpdateThemeInputDTO(
            theme_id=ThemeId(str(request.path_params["theme_id"])),
            label=payload.get("label"),
            description=payload.get("description"),
            is_active=payload.get("is_active"),
        )
        theme = await self.__update_theme_use_case.execute(theme_input)
        return HttpResponse(status_code=200, body=theme.to_dict())
