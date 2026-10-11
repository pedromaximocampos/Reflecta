from datetime import UTC, datetime, timedelta

import pytest

from src.modules.ai_processing.domain.entities import InboxEvent
from src.modules.ai_processing.domain.value_objects import InboxEventStatus


NOW = datetime(2026, 10, 9, 12, 0, tzinfo=UTC)


def _event(*, status: InboxEventStatus = InboxEventStatus.PROCESSING) -> InboxEvent:
    return InboxEvent(
        consumer_name="ai_processing.work_ingestion.v1",
        event_id="event-1",
        status=status,
        attempts=1,
        received_at=NOW,
        updated_at=NOW,
        lease_expires_at=(
            NOW + timedelta(minutes=5)
            if status is InboxEventStatus.PROCESSING
            else None
        ),
        processed_at=NOW if status is InboxEventStatus.PROCESSED else None,
    )


def test_processing_event_can_be_marked_processed() -> None:
    event = _event()

    event.mark_processed(now=NOW + timedelta(minutes=1))

    assert event.status is InboxEventStatus.PROCESSED
    assert event.processed_at == NOW + timedelta(minutes=1)
    assert event.lease_expires_at is None


def test_expired_processing_event_can_be_reclaimed_with_fencing_attempt() -> None:
    event = _event()
    reclaimed_at = NOW + timedelta(minutes=6)

    event.restart_processing(
        now=reclaimed_at,
        lease_expires_at=reclaimed_at + timedelta(minutes=5),
    )

    assert event.status is InboxEventStatus.PROCESSING
    assert event.attempts == 2
    assert event.lease_expires_at == reclaimed_at + timedelta(minutes=5)


def test_active_processing_lease_cannot_be_reclaimed() -> None:
    event = _event()

    with pytest.raises(ValueError, match="active inbox event lease"):
        event.restart_processing(
            now=NOW + timedelta(minutes=1),
            lease_expires_at=NOW + timedelta(minutes=6),
        )
