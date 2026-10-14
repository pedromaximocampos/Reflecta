from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from src.modules.ai_processing.application.exceptions import InboxClaimLostError
from src.modules.ai_processing.application.services import WorkIngestionInboxService
from src.modules.ai_processing.domain.value_objects import (
    InboxClaim,
    InboxClaimOutcome,
)


NOW = datetime(2026, 10, 9, 12, 0, tzinfo=UTC)


class _Clock:
    def now(self) -> datetime:
        return NOW


class _Uow:
    def __init__(self) -> None:
        self.inbox_event_repository = AsyncMock()
        self.commit = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


def _service(uow: _Uow) -> WorkIngestionInboxService:
    return WorkIngestionInboxService(
        uow=uow,
        clock=_Clock(),
        consumer_name="ai_processing.work_ingestion.v1",
    )


@pytest.mark.asyncio
async def test_claim_uses_consumer_namespace_and_commits() -> None:
    uow = _Uow()
    expected = InboxClaim(InboxClaimOutcome.CLAIMED, 1)
    uow.inbox_event_repository.claim.return_value = expected

    result = await _service(uow).claim("event-1", lease_seconds=300)

    assert result == expected
    call = uow.inbox_event_repository.claim.call_args.kwargs
    assert call["consumer_name"] == "ai_processing.work_ingestion.v1"
    assert call["event_id"] == "event-1"
    assert int((call["lease_expires_at"] - call["now"]).total_seconds()) == 300
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_renew_rejects_a_lost_fencing_attempt() -> None:
    uow = _Uow()
    uow.inbox_event_repository.renew_claim.return_value = False

    with pytest.raises(InboxClaimLostError):
        await _service(uow).renew(
            "event-1",
            expected_attempt=1,
            lease_seconds=300,
        )

    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_mark_processed_commits_the_durable_inbox_result() -> None:
    uow = _Uow()
    uow.inbox_event_repository.mark_processed.return_value = True

    await _service(uow).mark_processed("event-1", expected_attempt=2)

    uow.inbox_event_repository.mark_processed.assert_awaited_once()
    uow.commit.assert_awaited_once()
