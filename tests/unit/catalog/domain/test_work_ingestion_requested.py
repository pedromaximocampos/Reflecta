from datetime import datetime, timezone

from src.modules.auth.public.user_id import UserId
from src.modules.catalog.domain.events.work_ingestion_requested import (
    WorkIngestionRequested,
)
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)


def test_work_ingestion_requested_builds_outbox_event() -> None:
    occurred_at = datetime(2026, 10, 5, tzinfo=timezone.utc)
    created_at = datetime(2026, 10, 5, 0, 1, tzinfo=timezone.utc)
    event = WorkIngestionRequested(
        ingestion_id=WorkIngestionId("01K6G7VPK3NMZ32D7KFV63J0QF"),
        work_id=WorkId("01K6G7VPK3NMZ32D7KFV63J0QG"),
        requested_by=UserId("01K6G7VPK3NMZ32D7KFV63J0QH"),
        document_location=WorkDocumentLocation(
            bucket="reflecta-works-dev",
            object_key="works/work-id/source/document-id.pdf",
        ),
        occurred_at=occurred_at,
    )

    outbox_event = event.to_outbox_event(
        event_id="01K6G7VPK3NMZ32D7KFV63J0QJ",
        created_at=created_at,
    )

    assert outbox_event.event_type.value == "catalog.work.ingestion.requested"
    assert outbox_event.event_occurred_at == occurred_at
    assert outbox_event.created_at == created_at
    assert outbox_event.payload == {
        "ingestion_id": "01K6G7VPK3NMZ32D7KFV63J0QF",
        "work_id": "01K6G7VPK3NMZ32D7KFV63J0QG",
        "requested_by": "01K6G7VPK3NMZ32D7KFV63J0QH",
        "s3_bucket": "reflecta-works-dev",
        "s3_object_key": "works/work-id/source/document-id.pdf",
        "occurred_at": occurred_at.isoformat(),
    }
