from typing import Protocol

from .dto import GetWorkDocumentAccessInputDTO, GetWorkDocumentAccessOutputDTO


class IGetWorkDocumentAccessUseCase(Protocol):
    async def execute(
        self,
        ingestion_input: GetWorkDocumentAccessInputDTO,
    ) -> GetWorkDocumentAccessOutputDTO: ...
