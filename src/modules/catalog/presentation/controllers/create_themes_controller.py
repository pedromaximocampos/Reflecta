from src.modules.catalog.application.use_cases.create_themes.dto import CreateThemesInputDTO
from src.modules.catalog.application.use_cases.create_themes.icreate_themes_use_case import ICreateThemesUseCase
from src.shared.presentation.http_types import HttpResponse, HttpRequest
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class CreateThemesController(IControllerInterface):
    def __init__(self, create_themes_use_case: ICreateThemesUseCase) -> None:
        self.__create_themes_use_case = create_themes_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:

        if request.body is None:
            raise ValueError("Request body cannot be None")

        themes_data_dto = CreateThemesInputDTO.to_class(request.body)

        created_themes_dto = await self.__create_themes_use_case.execute(themes_data_dto)

        return HttpResponse(
            status_code=201,
            body=created_themes_dto.to_dict(),
        )
