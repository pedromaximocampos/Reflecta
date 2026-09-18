from typing import Protocol

from src.modules.catalog.public.theme_id import ThemeId


class IDeleteThemeByIdUseCase(Protocol):
    async def execute(self, theme_id: ThemeId) -> None: ...
