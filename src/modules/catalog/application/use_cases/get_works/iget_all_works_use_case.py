from typing import Protocol

from src.modules.catalog.application.dto import WorksOutputDTO


class IGetAllWorksUseCase(Protocol):
    async def execute(self) -> WorksOutputDTO: ...
