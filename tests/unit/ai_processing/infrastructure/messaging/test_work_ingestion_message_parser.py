import json

import pytest

from src.modules.ai_processing.infrastructure.messaging.aws_sqs.message_parser import (
    WorkIngestionRequestedMessageParser,
)


def make_message() -> dict:
    return {
        "Body": json.dumps(
            {
                "ingestion_id": "01K72VD7R6J4J6YB6PXG1X9Y12",
                "work_id": "01K72VD7R6J4J6YB6PXG1X9Y13",
                "requested_by": "01K72VD7R6J4J6YB6PXG1X9Y14",
                "s3_bucket": "reflecta-works-dev",
                "s3_object_key": "works/work/source/book.pdf",
                "occurred_at": "2026-10-08T12:00:00+00:00",
            }
        ),
        "MessageAttributes": {
            "id": {"StringValue": "01K72VD7R6J4J6YB6PXG1X9Y15"},
            "event_type": {"StringValue": "catalog.work.ingestion.requested"},
        },
        "Attributes": {"ApproximateReceiveCount": "3"},
    }


def test_parses_raw_sns_message_delivered_by_sqs() -> None:
    parsed = WorkIngestionRequestedMessageParser().parse(make_message())

    assert parsed.event_id == "01K72VD7R6J4J6YB6PXG1X9Y15"
    assert parsed.ingestion_id.value == "01K72VD7R6J4J6YB6PXG1X9Y12"
    assert parsed.source_document.object_key == "works/work/source/book.pdf"
    assert parsed.delivery_attempt == 3


def test_rejects_an_event_for_another_consumer() -> None:
    message = make_message()
    message["MessageAttributes"]["event_type"]["StringValue"] = (
        "emails.verification.requested"
    )

    with pytest.raises(ValueError, match="Unsupported event type"):
        WorkIngestionRequestedMessageParser().parse(message)
