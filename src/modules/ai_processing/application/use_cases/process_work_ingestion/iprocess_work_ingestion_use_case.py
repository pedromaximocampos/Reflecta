from typing import Protocol

from .dto import ProcessWorkIngestionInputDTO, ProcessWorkIngestionOutputDTO


class IProcessWorkIngestionUseCase(Protocol):
    async def execute(
        self,
        ingestion_input: ProcessWorkIngestionInputDTO,
    ) -> ProcessWorkIngestionOutputDTO: ...
