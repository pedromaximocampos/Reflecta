from typing import Protocol

from src.modules.catalog.application.dto import WorkOutputDTO
from src.modules.catalog.public.work_id import WorkId


class IGetWorkByIdUseCase(Protocol):
    async def execute(self, work_id: WorkId) -> WorkOutputDTO: ...
