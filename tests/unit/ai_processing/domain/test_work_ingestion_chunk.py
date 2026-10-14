from datetime import datetime, timedelta, timezone

import pytest

from src.modules.ai_processing.domain.entities import WorkIngestionChunk
from src.modules.ai_processing.domain.exceptions import (
    InvalidWorkIngestionChunkTransitionError,
)
from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.modules.ai_processing.public import WorkIngestionChunkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


def make_chunk() -> WorkIngestionChunk:
    created_at = datetime(2026, 10, 8, tzinfo=timezone.utc)
    return WorkIngestionChunk(
        id=WorkIngestionChunkId("01K72VD7R6J4J6YB6PXG1X9Y11"),
        ingestion_id=WorkIngestionId("01K72VD7R6J4J6YB6PXG1X9Y12"),
        chunk_index=0,
        start_page=1,
        end_page=2,
        start_offset=0,
        end_offset=800,
        content_sha256="a" * 64,
        chunker_version="v1",
        created_at=created_at,
        updated_at=created_at,
    )


def test_chunk_follows_processing_lifecycle() -> None:
    chunk = make_chunk()
    now = datetime(2026, 10, 8, 1, tzinfo=timezone.utc)

    chunk.mark_processing(
        now=now,
        lease_expires_at=now + timedelta(minutes=5),
    )
    chunk.mark_completed(now=now + timedelta(minutes=1))

    assert chunk.status is WorkIngestionChunkStatus.COMPLETED
    assert chunk.attempts == 1
    assert chunk.lease_expires_at is None


def test_failed_chunk_can_be_claimed_again() -> None:
    chunk = make_chunk()
    now = datetime(2026, 10, 8, 1, tzinfo=timezone.utc)

    chunk.mark_processing(
        now=now,
        lease_expires_at=now + timedelta(minutes=5),
    )
    chunk.mark_failed(
        now=now + timedelta(seconds=10),
        error_code="MODEL_TIMEOUT",
        error_message="The model request timed out.",
    )
    chunk.mark_processing(
        now=now + timedelta(minutes=1),
        lease_expires_at=now + timedelta(minutes=6),
    )

    assert chunk.status is WorkIngestionChunkStatus.PROCESSING
    assert chunk.attempts == 2
    assert chunk.error_code is None


def test_expired_processing_lease_can_be_reclaimed() -> None:
    chunk = make_chunk()
    now = datetime(2026, 10, 8, 1, tzinfo=timezone.utc)
    chunk.mark_processing(
        now=now,
        lease_expires_at=now + timedelta(minutes=1),
    )

    chunk.mark_processing(
        now=now + timedelta(minutes=2),
        lease_expires_at=now + timedelta(minutes=7),
    )

    assert chunk.attempts == 2


def test_active_processing_lease_cannot_be_reclaimed() -> None:
    chunk = make_chunk()
    now = datetime(2026, 10, 8, 1, tzinfo=timezone.utc)
    chunk.mark_processing(
        now=now,
        lease_expires_at=now + timedelta(minutes=5),
    )

    with pytest.raises(InvalidWorkIngestionChunkTransitionError):
        chunk.mark_processing(
            now=now + timedelta(minutes=1),
            lease_expires_at=now + timedelta(minutes=6),
        )
