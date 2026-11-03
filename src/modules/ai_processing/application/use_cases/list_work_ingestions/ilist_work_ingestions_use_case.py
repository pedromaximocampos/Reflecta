from typing import Protocol

from .dto import WorkIngestionsOutputDTO


class IListWorkIngestionsUseCase(Protocol):
    async def execute(self, *, limit: int) -> WorkIngestionsOutputDTO: ...
