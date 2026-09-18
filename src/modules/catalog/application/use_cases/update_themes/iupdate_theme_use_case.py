from typing import Protocol

from src.modules.catalog.application.dto.theme import ThemeOutputDTO
from src.modules.catalog.application.use_cases.update_themes.dto import (
    UpdateThemeInputDTO,
)


class IUpdateThemeUseCase(Protocol):
    async def execute(self, theme_input: UpdateThemeInputDTO) -> ThemeOutputDTO: ...
