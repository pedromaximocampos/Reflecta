from src.shared.presentation.http_types import HttpResponse, HttpRequest
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class CreateThemesController(IControllerInterface):
    def __init__(self, create_themes_use_case):
        self.create_themes_use_case = create_themes_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        themes_data = request.get_json()
        created_themes = self.create_themes_use_case.execute(themes_data)
        return {"created_themes": created_themes}, 201