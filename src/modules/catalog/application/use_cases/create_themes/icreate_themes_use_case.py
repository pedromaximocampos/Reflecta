from typing import Protocol

from modules.catalog.application.use_cases.create_themes.dto import CreateThemesInputDTO, CreateThemesOutputDTO


class ICreateThemesUseCase(Protocol):

    async def execute(self, themes_input: CreateThemesInputDTO) -> CreateThemesOutputDTO:
        ...