from typing import Protocol

from .dto import (
    ReprocessWorkIngestionInputDTO,
    ReprocessWorkIngestionOutputDTO,
)


class IReprocessWorkIngestionUseCase(Protocol):
    async def execute(
        self,
        ingestion_input: ReprocessWorkIngestionInputDTO,
    ) -> ReprocessWorkIngestionOutputDTO: ...
