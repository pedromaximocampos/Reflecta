from datetime import datetime, timezone

import pytest

from src.modules.auth.public.user_id import UserId
from src.modules.catalog.domain.entities.work_ingestion import WorkIngestion
from src.modules.catalog.domain.exceptions.work_exceptions import (
    InvalidWorkIngestionTransitionError,
)
from src.modules.catalog.domain.value_objects.work_ingestion_status import (
    WorkIngestionStatus,
)
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


def make_ingestion() -> WorkIngestion:
    return WorkIngestion(
        id=WorkIngestionId("01K6G7VPK3NMZ32D7KFV63J0QF"),
        work_id=WorkId("01K6G7VPK3NMZ32D7KFV63J0QG"),
        requested_by=UserId("01K6G7VPK3NMZ32D7KFV63J0QH"),
        document_location=WorkDocumentLocation(
            bucket="reflecta-works-dev",
            object_key="works/work-id/source/document-id.pdf",
        ),
        created_at=datetime(2026, 10, 5, tzinfo=timezone.utc),
    )


def test_work_ingestion_follows_processing_lifecycle() -> None:
    ingestion = make_ingestion()
    processing_at = datetime(2026, 10, 5, 1, tzinfo=timezone.utc)
    reviewed_at = datetime(2026, 10, 5, 2, tzinfo=timezone.utc)

    ingestion.mark_processing(now=processing_at)
    ingestion.mark_pending_review(now=reviewed_at)
    ingestion.mark_completed(now=reviewed_at)

    assert ingestion.status is WorkIngestionStatus.COMPLETED
    assert ingestion.attempts == 1
    assert ingestion.started_at == processing_at
    assert ingestion.finished_at == reviewed_at


def test_work_ingestion_can_retry_after_failure() -> None:
    ingestion = make_ingestion()
    now = datetime(2026, 10, 5, 1, tzinfo=timezone.utc)

    ingestion.mark_processing(now=now)
    ingestion.mark_failed(
        now=now,
        error_code="PDF_EXTRACTION_FAILED",
        error_message="The PDF could not be extracted.",
    )
    ingestion.mark_processing(now=now)

    assert ingestion.status is WorkIngestionStatus.PROCESSING
    assert ingestion.attempts == 2
    assert ingestion.error_code is None
    assert ingestion.error_message is None


def test_work_ingestion_can_finish_when_all_chunks_complete_after_a_failure() -> None:
    ingestion = make_ingestion()
    now = datetime(2026, 10, 5, 1, tzinfo=timezone.utc)

    ingestion.mark_processing(now=now)
    ingestion.mark_failed(
        now=now,
        error_code="TRANSIENT_PROVIDER_ERROR",
        error_message="A chunk failed while another worker was still active.",
    )
    ingestion.mark_pending_review(now=now)

    assert ingestion.status is WorkIngestionStatus.PENDING_REVIEW
    assert ingestion.error_code is None
    assert ingestion.error_message is None


def test_work_ingestion_rejects_invalid_transition() -> None:
    ingestion = make_ingestion()

    with pytest.raises(InvalidWorkIngestionTransitionError):
        ingestion.mark_completed(now=datetime(2026, 10, 5, 1, tzinfo=timezone.utc))
