from typing import Protocol

from src.modules.catalog.application.use_cases.create_work.dto import (
    CreateWorkInputDTO,
    CreateWorkOutputDTO,
)


class ICreateWorkUseCase(Protocol):
    async def execute(self, work_input: CreateWorkInputDTO) -> CreateWorkOutputDTO: ...
