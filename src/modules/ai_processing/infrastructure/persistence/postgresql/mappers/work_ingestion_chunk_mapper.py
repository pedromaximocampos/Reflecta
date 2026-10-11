from src.modules.ai_processing.domain.entities import WorkIngestionChunk
from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.modules.ai_processing.infrastructure.persistence.postgresql.models import (
    WorkIngestionChunkModel,
)
from src.modules.ai_processing.public import WorkIngestionChunkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class WorkIngestionChunkMapper(IMapper[WorkIngestionChunkModel, WorkIngestionChunk]):
    def to_entity(self, model: WorkIngestionChunkModel) -> WorkIngestionChunk:
        return WorkIngestionChunk(
            id=WorkIngestionChunkId(model.id),
            ingestion_id=WorkIngestionId(model.ingestion_id),
            chunk_index=model.chunk_index,
            start_page=model.start_page,
            end_page=model.end_page,
            start_offset=model.start_offset,
            end_offset=model.end_offset,
            content_sha256=model.content_sha256,
            chunker_version=model.chunker_version,
            created_at=model.created_at,
            updated_at=model.updated_at,
            status=WorkIngestionChunkStatus(model.status),
            attempts=model.attempts,
            started_at=model.started_at,
            finished_at=model.finished_at,
            lease_expires_at=model.lease_expires_at,
            error_code=model.error_code,
            error_message=model.error_message,
        )

    def to_model(self, entity: WorkIngestionChunk) -> WorkIngestionChunkModel:
        return WorkIngestionChunkModel(
            id=entity.id.value,
            ingestion_id=entity.ingestion_id.value,
            chunk_index=entity.chunk_index,
            start_page=entity.start_page,
            end_page=entity.end_page,
            start_offset=entity.start_offset,
            end_offset=entity.end_offset,
            content_sha256=entity.content_sha256,
            chunker_version=entity.chunker_version,
            status=entity.status.value,
            attempts=entity.attempts,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            started_at=entity.started_at,
            finished_at=entity.finished_at,
            lease_expires_at=entity.lease_expires_at,
            error_code=entity.error_code,
            error_message=entity.error_message,
        )
