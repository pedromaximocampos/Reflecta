from typing import Protocol

from src.modules.catalog.application.dto.theme import ThemeOutputDTO
from src.modules.catalog.public.theme_id import ThemeId


class IGetThemeByIdUseCase(Protocol):
    async def execute(self, theme_id: ThemeId) -> ThemeOutputDTO: ...
