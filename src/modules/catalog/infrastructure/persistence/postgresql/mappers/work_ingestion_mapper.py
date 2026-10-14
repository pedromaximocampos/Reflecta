from src.modules.auth.public.user_id import UserId
from src.modules.catalog.domain.entities.work_ingestion import WorkIngestion
from src.modules.catalog.domain.value_objects.work_ingestion_status import (
    WorkIngestionStatus,
)
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)
from src.modules.catalog.infrastructure.persistence.postgresql.models.work_ingestion_model import (
    WorkIngestionModel,
)
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class WorkIngestionMapper(IMapper[WorkIngestionModel, WorkIngestion]):
    def to_entity(self, model: WorkIngestionModel) -> WorkIngestion:
        return WorkIngestion(
            id=WorkIngestionId(model.id),
            work_id=WorkId(model.work_id),
            requested_by=UserId(model.requested_by),
            document_location=WorkDocumentLocation(
                bucket=model.s3_bucket,
                object_key=model.s3_object_key,
            ),
            status=WorkIngestionStatus(model.status),
            attempts=model.attempts,
            created_at=model.created_at,
            started_at=model.started_at,
            finished_at=model.finished_at,
            error_code=model.error_code,
            error_message=model.error_message,
        )

    def to_model(self, entity: WorkIngestion) -> WorkIngestionModel:
        return WorkIngestionModel(
            id=entity.id.value,
            work_id=entity.work_id.value,
            requested_by=entity.requested_by.value,
            s3_bucket=entity.document_location.bucket,
            s3_object_key=entity.document_location.object_key,
            status=entity.status.value,
            attempts=entity.attempts,
            created_at=entity.created_at,
            started_at=entity.started_at,
            finished_at=entity.finished_at,
            error_code=entity.error_code,
            error_message=entity.error_message,
        )
