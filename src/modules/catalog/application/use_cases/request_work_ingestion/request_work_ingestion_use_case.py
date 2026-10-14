import logging

from src.modules.catalog.application.ports.storage.iwork_document_storage import (
    IWorkDocumentStorage,
)
from src.modules.catalog.application.use_cases.request_work_ingestion.dto import (
    RequestWorkIngestionInputDTO,
    RequestWorkIngestionOutputDTO,
)
from src.modules.catalog.application.use_cases.request_work_ingestion.irequest_work_ingestion_use_case import (
    IRequestWorkIngestionUseCase,
)
from src.modules.catalog.domain.entities.work_ingestion import WorkIngestion
from src.modules.catalog.domain.events.work_ingestion_requested import (
    WorkIngestionRequested,
)
from src.modules.catalog.domain.exceptions.work_exceptions import (
    InvalidWorkDocumentError,
    WorkNotFoundError,
)
from src.modules.catalog.domain.ports.unit_of_work.icatalog_graph_unit_of_work import (
    ICatalogGraphUnitOfWork,
)
from src.modules.catalog.domain.ports.unit_of_work.icatalog_sql_unit_of_work import (
    ICatalogSQLUnitOfWork,
)
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.modules.internal_events.public import IOutboxService
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


_LOGGER = logging.getLogger(__name__)


class RequestWorkIngestionUseCase(IRequestWorkIngestionUseCase):
    def __init__(
        self,
        catalog_graph_uow: ICatalogGraphUnitOfWork,
        catalog_sql_uow: ICatalogSQLUnitOfWork,
        work_document_storage: IWorkDocumentStorage,
        outbox_service: IOutboxService,
        ulid_generator: IULIDGenerator,
        clock: IClock,
    ) -> None:
        self.__catalog_graph_uow = catalog_graph_uow
        self.__catalog_sql_uow = catalog_sql_uow
        self.__work_document_storage = work_document_storage
        self.__outbox_service = outbox_service
        self.__ulid_generator = ulid_generator
        self.__clock = clock

    async def execute(
        self,
        ingestion_input: RequestWorkIngestionInputDTO,
    ) -> RequestWorkIngestionOutputDTO:
        self._validate_document(ingestion_input)
        await self._ensure_work_exists(ingestion_input.work_id)

        ingestion_id = WorkIngestionId(self.__ulid_generator.generate_ulid())
        object_key = self._build_object_key(
            work_id=ingestion_input.work_id,
            ingestion_id=ingestion_id,
        )
        stored_document = await self.__work_document_storage.upload(
            object_key=object_key,
            content=ingestion_input.content,
            content_type=ingestion_input.content_type,
            size_bytes=ingestion_input.size_bytes,
        )

        database_committed = False
        try:
            created_at = self.__clock.now()
            ingestion = WorkIngestion(
                id=ingestion_id,
                work_id=ingestion_input.work_id,
                requested_by=ingestion_input.requested_by,
                document_location=stored_document.location,
                created_at=created_at,
            )

            async with self.__catalog_sql_uow as uow:
                created_ingestion = await uow.work_ingestion_repository.create(
                    ingestion
                )
                event = WorkIngestionRequested(
                    ingestion_id=created_ingestion.id,
                    work_id=created_ingestion.work_id,
                    requested_by=created_ingestion.requested_by,
                    document_location=created_ingestion.document_location,
                    occurred_at=created_ingestion.created_at,
                )
                await self.__outbox_service.persist_event(
                    event,
                    uow.outbox_repository,
                )
                await uow.commit()
                database_committed = True

            return RequestWorkIngestionOutputDTO.from_entity(created_ingestion)
        except Exception:
            if not database_committed:
                await self._compensate_document_upload(stored_document.location)
            raise

    async def _ensure_work_exists(self, work_id: WorkId) -> None:
        async with self.__catalog_graph_uow as uow:
            work = await uow.work_repository.get_work_by_id(work_id)
            if work is None:
                raise WorkNotFoundError(work_id.value)

    async def _compensate_document_upload(
        self,
        location: WorkDocumentLocation,
    ) -> None:
        try:
            await self.__work_document_storage.delete(location=location)
        except Exception:
            _LOGGER.exception(
                "Failed to compensate catalog work document upload: "
                "bucket=%s object_key=%s",
                location.bucket,
                location.object_key,
            )

    @staticmethod
    def _build_object_key(
        *,
        work_id: WorkId,
        ingestion_id: WorkIngestionId,
    ) -> str:
        return f"works/{work_id.value}/source/{ingestion_id.value}.pdf"

    @staticmethod
    def _validate_document(
        ingestion_input: RequestWorkIngestionInputDTO,
    ) -> None:
        if ingestion_input.content_type.lower() != "application/pdf":
            raise InvalidWorkDocumentError("The work document must be a PDF.")
        if not ingestion_input.filename.lower().endswith(".pdf"):
            raise InvalidWorkDocumentError("The work document must use a .pdf extension.")
        if ingestion_input.size_bytes <= 0:
            raise InvalidWorkDocumentError("The work document must not be empty.")
        if not ingestion_input.content.seekable():
            raise InvalidWorkDocumentError("The work document stream must be seekable.")

        try:
            ingestion_input.content.seek(0, 2)
            actual_size = ingestion_input.content.tell()
            ingestion_input.content.seek(0)
            header = ingestion_input.content.read(5)
            ingestion_input.content.seek(0)
        except (OSError, ValueError) as error:
            raise InvalidWorkDocumentError(
                "The work document could not be inspected."
            ) from error

        if actual_size != ingestion_input.size_bytes:
            raise InvalidWorkDocumentError("The work document size is inconsistent.")
        if header != b"%PDF-":
            raise InvalidWorkDocumentError("The work document content is not a PDF.")
