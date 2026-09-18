from typing import Protocol

from src.modules.catalog.application.dto.theme import ThemesOutputDTO


class IGetAllThemesUseCase(Protocol):
    async def execute(self) -> ThemesOutputDTO: ...
