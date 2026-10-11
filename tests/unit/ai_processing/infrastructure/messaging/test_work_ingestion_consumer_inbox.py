import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.ai_processing.application.exceptions import WorkPassageAnalysisError
from src.modules.ai_processing.domain.value_objects import (
    InboxClaim,
    InboxClaimOutcome,
)
from src.modules.ai_processing.infrastructure.messaging.aws_sqs.configs import (
    WorkIngestionSQSSettings,
)
from src.modules.ai_processing.infrastructure.messaging.aws_sqs.work_ingestion_consumer import (
    SQSWorkIngestionConsumerWorker,
)


def _message() -> dict:
    return {
        "MessageId": "sqs-message-1",
        "ReceiptHandle": "receipt-1",
        "Body": json.dumps(
            {
                "ingestion_id": "01K72VD7R6J4J6YB6PXG1X9Y12",
                "work_id": "01K72VD7R6J4J6YB6PXG1X9Y13",
                "requested_by": "01K72VD7R6J4J6YB6PXG1X9Y14",
                "s3_bucket": "reflecta-works-dev",
                "s3_object_key": "works/work/source/book.pdf",
                "occurred_at": "2026-10-09T12:00:00+00:00",
            }
        ),
        "MessageAttributes": {
            "id": {"StringValue": "01K72VD7R6J4J6YB6PXG1X9Y15"},
            "event_type": {
                "StringValue": "catalog.work.ingestion.requested"
            },
        },
        "Attributes": {"ApproximateReceiveCount": "3"},
    }


def _worker(outcome: InboxClaimOutcome):
    client = SimpleNamespace(
        delete_message=MagicMock(),
        change_message_visibility=MagicMock(),
    )
    inbox = SimpleNamespace(
        claim=AsyncMock(return_value=InboxClaim(outcome, 1)),
        renew=AsyncMock(),
        mark_processed=AsyncMock(),
        mark_failed=AsyncMock(return_value=True),
    )
    use_case = SimpleNamespace(execute=AsyncMock())
    settings = WorkIngestionSQSSettings(
        aws_region="us-east-1",
        queue_url="https://sqs.example.test/work-ingestions",
        visibility_timeout_seconds=300,
        heartbeat_interval_seconds=120,
    )
    worker = SQSWorkIngestionConsumerWorker(
        client=client,
        settings=settings,
        use_case=use_case,
        inbox=inbox,
    )
    return worker, client, inbox, use_case


@pytest.mark.asyncio
async def test_claimed_event_is_processed_before_sqs_acknowledgement() -> None:
    worker, client, inbox, use_case = _worker(InboxClaimOutcome.CLAIMED)

    await worker.handle_message(_message())

    use_case.execute.assert_awaited_once()
    inbox.mark_processed.assert_awaited_once_with(
        "01K72VD7R6J4J6YB6PXG1X9Y15",
        expected_attempt=1,
    )
    inbox.mark_failed.assert_not_awaited()
    client.delete_message.assert_called_once()


@pytest.mark.asyncio
async def test_processed_duplicate_skips_use_case_and_is_acknowledged() -> None:
    worker, client, inbox, use_case = _worker(
        InboxClaimOutcome.ALREADY_PROCESSED
    )

    await worker.handle_message(_message())

    use_case.execute.assert_not_awaited()
    inbox.mark_processed.assert_not_awaited()
    client.delete_message.assert_called_once()


@pytest.mark.asyncio
async def test_busy_duplicate_is_not_processed_or_acknowledged() -> None:
    worker, client, inbox, use_case = _worker(InboxClaimOutcome.BUSY)

    await worker.handle_message(_message())

    use_case.execute.assert_not_awaited()
    inbox.mark_processed.assert_not_awaited()
    client.delete_message.assert_not_called()


@pytest.mark.asyncio
async def test_failure_is_recorded_before_sqs_retry_is_scheduled() -> None:
    worker, client, inbox, use_case = _worker(InboxClaimOutcome.CLAIMED)
    use_case.execute.side_effect = RuntimeError("provider unavailable")

    await worker.handle_message(_message())

    inbox.mark_failed.assert_awaited_once_with(
        "01K72VD7R6J4J6YB6PXG1X9Y15",
        expected_attempt=1,
        error_code="RuntimeError",
    )
    client.delete_message.assert_not_called()
    client.change_message_visibility.assert_called_once_with(
        QueueUrl="https://sqs.example.test/work-ingestions",
        ReceiptHandle="receipt-1",
        VisibilityTimeout=240,
    )


@pytest.mark.asyncio
async def test_failure_records_sanitized_analysis_error_code() -> None:
    worker, _, inbox, use_case = _worker(InboxClaimOutcome.CLAIMED)
    use_case.execute.side_effect = WorkPassageAnalysisError(
        "Work passage analysis failed.",
        code="quote_not_found",
    )

    await worker.handle_message(_message())

    inbox.mark_failed.assert_awaited_once_with(
        "01K72VD7R6J4J6YB6PXG1X9Y15",
        expected_attempt=1,
        error_code="quote_not_found",
    )


@pytest.mark.asyncio
async def test_sqs_delete_failure_does_not_revert_processed_inbox() -> None:
    worker, client, inbox, _ = _worker(InboxClaimOutcome.CLAIMED)
    client.delete_message.side_effect = RuntimeError("temporary SQS failure")

    await worker.handle_message(_message())

    inbox.mark_processed.assert_awaited_once()
    inbox.mark_failed.assert_not_awaited()
