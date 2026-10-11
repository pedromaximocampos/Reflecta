from datetime import datetime, timezone

from src.modules.auth.public.user_id import UserId
from src.modules.catalog.domain.entities.work_ingestion import WorkIngestion
from src.modules.catalog.domain.value_objects.work_ingestion_status import (
    WorkIngestionStatus,
)
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)
from src.modules.catalog.infrastructure.persistence.postgresql.mappers.work_ingestion_mapper import (
    WorkIngestionMapper,
)
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


def test_work_ingestion_mapper_round_trip() -> None:
    created_at = datetime(2026, 10, 5, tzinfo=timezone.utc)
    entity = WorkIngestion(
        id=WorkIngestionId("01K6G7VPK3NMZ32D7KFV63J0QF"),
        work_id=WorkId("01K6G7VPK3NMZ32D7KFV63J0QG"),
        requested_by=UserId("01K6G7VPK3NMZ32D7KFV63J0QH"),
        document_location=WorkDocumentLocation(
            bucket="reflecta-works-dev",
            object_key="works/work-id/source/document-id.pdf",
        ),
        status=WorkIngestionStatus.PENDING,
        created_at=created_at,
    )
    mapper = WorkIngestionMapper()

    mapped_entity = mapper.to_entity(mapper.to_model(entity))

    assert mapped_entity.id == entity.id
    assert mapped_entity.work_id == entity.work_id
    assert mapped_entity.requested_by == entity.requested_by
    assert mapped_entity.document_location == entity.document_location
    assert mapped_entity.status is WorkIngestionStatus.PENDING
