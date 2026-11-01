from typing import Protocol

from src.modules.catalog.application.dto import WorkOutputDTO
from src.modules.catalog.application.use_cases.update_work_cover.dto import (
    RemoveWorkCoverInputDTO,
    ReplaceWorkCoverInputDTO,
)


class IReplaceWorkCoverUseCase(Protocol):
    async def execute(
        self,
        work_input: ReplaceWorkCoverInputDTO,
    ) -> WorkOutputDTO: ...


class IRemoveWorkCoverUseCase(Protocol):
    async def execute(
        self,
        work_input: RemoveWorkCoverInputDTO,
    ) -> WorkOutputDTO: ...
