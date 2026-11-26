from datetime import datetime, timezone

import pytest

from src.modules.operations.infrastructure.work_ingestion_diagnostics_gateway import (
    CloudWatchOperationalLogGateway,
)


class FakeCloudWatchLogsClient:
    def __init__(self) -> None:
        self.calls = []

    def filter_log_events(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "events": [
                {
                    "eventId": "event-1",
                    "timestamp": 1_796_153_400_000,
                    "message": (
                        "ingestion_id=01MTESTINGESTION00000000 "
                        "token=secret-value Bearer access.token.value"
                    ),
                }
            ]
        }


@pytest.mark.asyncio
async def test_queries_bounded_correlated_logs_and_redacts_secrets() -> None:
    gateway = object.__new__(CloudWatchOperationalLogGateway)
    client = FakeCloudWatchLogsClient()
    gateway._client = client
    gateway._log_group = "/reflecta/demo/application"
    detail = {
        "source": "work_ingestion",
        "id": "01MTESTFAILURE000000000000",
        "entity_id": "01MTESTINGESTION00000000",
        "related_id": "01MTESTWORK0000000000000",
        "occurred_at": datetime(2026, 11, 25, 21, tzinfo=timezone.utc).isoformat(),
        "failure_attempt": None,
    }

    result = await gateway.list_logs(detail)

    assert result["retention_days"] == 14
    assert len(result["logs"]) == 1
    assert "secret-value" not in result["logs"][0]["message"]
    assert "access.token.value" not in result["logs"][0]["message"]
    assert client.calls
    for call in client.calls:
        assert call["logGroupName"] == "/reflecta/demo/application"
        assert call["logStreamNames"] == ["worker-work-ingestion"]
        assert call["endTime"] - call["startTime"] == 600_000
        assert call["limit"] == 100
