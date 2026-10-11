from typing import Protocol

from .dto import RequestWorkIngestionInputDTO, RequestWorkIngestionOutputDTO


class IRequestWorkIngestionUseCase(Protocol):
    async def execute(
        self,
        ingestion_input: RequestWorkIngestionInputDTO,
    ) -> RequestWorkIngestionOutputDTO: ...
