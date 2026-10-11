from datetime import datetime, timezone

from src.modules.ai_processing.domain.entities import WorkIngestionChunk
from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.modules.ai_processing.infrastructure.persistence.postgresql.mappers import (
    WorkIngestionChunkMapper,
)
from src.modules.ai_processing.public import WorkIngestionChunkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


def test_work_ingestion_chunk_mapper_round_trip() -> None:
    created_at = datetime(2026, 10, 8, tzinfo=timezone.utc)
    entity = WorkIngestionChunk(
        id=WorkIngestionChunkId("01K72VD7R6J4J6YB6PXG1X9Y11"),
        ingestion_id=WorkIngestionId("01K72VD7R6J4J6YB6PXG1X9Y12"),
        chunk_index=3,
        start_page=5,
        end_page=6,
        start_offset=2400,
        end_offset=3200,
        content_sha256="b" * 64,
        chunker_version="v1",
        created_at=created_at,
        updated_at=created_at,
    )
    mapper = WorkIngestionChunkMapper()

    mapped = mapper.to_entity(mapper.to_model(entity))

    assert mapped.id == entity.id
    assert mapped.ingestion_id == entity.ingestion_id
    assert mapped.chunk_index == 3
    assert mapped.status is WorkIngestionChunkStatus.PENDING
    assert mapped.content_sha256 == entity.content_sha256
