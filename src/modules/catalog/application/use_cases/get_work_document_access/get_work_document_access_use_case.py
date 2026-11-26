from src.modules.catalog.application.ports.storage import IWorkDocumentStorage
from src.modules.catalog.domain.exceptions.work_exceptions import (
    WorkIngestionNotFoundError,
)
from src.modules.catalog.domain.ports.unit_of_work import ICatalogSQLUnitOfWork

from .dto import GetWorkDocumentAccessInputDTO, GetWorkDocumentAccessOutputDTO
from .iget_work_document_access_use_case import IGetWorkDocumentAccessUseCase


class GetWorkDocumentAccessUseCase(IGetWorkDocumentAccessUseCase):
    def __init__(
        self,
        catalog_sql_uow: ICatalogSQLUnitOfWork,
        work_document_storage: IWorkDocumentStorage,
        *,
        expires_in_seconds: int,
    ) -> None:
        if expires_in_seconds < 60 or expires_in_seconds > 3600:
            raise ValueError("Work document access TTL must be between 60 and 3600 seconds.")
        self._catalog_sql_uow = catalog_sql_uow
        self._work_document_storage = work_document_storage
        self._expires_in_seconds = expires_in_seconds

    async def execute(
        self,
        ingestion_input: GetWorkDocumentAccessInputDTO,
    ) -> GetWorkDocumentAccessOutputDTO:
        async with self._catalog_sql_uow as uow:
            ingestion = await uow.work_ingestion_repository.find_by_id(
                ingestion_input.ingestion_id
            )
        if ingestion is None:
            raise WorkIngestionNotFoundError(ingestion_input.ingestion_id.value)
        url = await self._work_document_storage.create_read_url(
            location=ingestion.document_location
        )
        return GetWorkDocumentAccessOutputDTO(
            ingestion_id=ingestion.id,
            url=url,
            expires_in_seconds=self._expires_in_seconds,
        )
