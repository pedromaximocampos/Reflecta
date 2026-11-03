from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import pytest
from sqlalchemy.dialects import postgresql
from src.modules.operations.application.diagnostics import (
    safe_diagnostic,
    safe_outbox_diagnostic,
)
from src.modules.operations.infrastructure.failure_gateway import OperationalFailureGateway


@pytest.mark.parametrize("raw", [None, "secret text", "{}", "null", "[]", "bad json",
    '{"code":"secret-value","message":"secret-text","attempts":true}',
    '{"code":123,"message":"secret-text"}'])
def test_unknown_diagnostics_never_expose_saved_values(raw):
    result = safe_diagnostic(raw=raw)
    assert result["code"] == "unknown_error"
    assert "secret" not in str(result)


def test_known_code_uses_fixed_message_even_when_saved_message_contains_secrets():
    result = safe_diagnostic(raw='{"code":"provider_timeout","message":"secret key and journal text","attempts":2}')
    assert result == {"code": "provider_timeout", "message": "O provedor excedeu o tempo limite da análise.", "attempts": 2}


@pytest.mark.parametrize("attempts", [True, -1, 1000001, "2"])
def test_invalid_attempts_are_not_returned(attempts):
    assert safe_diagnostic(code="provider_timeout", attempts=attempts)["attempts"] is None


@pytest.mark.parametrize(
    ("raw", "code"),
    [
        ("Error loading SSO token: token has expired", "aws_credentials_unavailable"),
        ("AccessDenied: not authorized to perform sns:Publish", "aws_access_denied"),
        ("EndpointConnectionError: could not connect to the endpoint", "event_provider_unreachable"),
        ("secret provider message", "event_delivery_failed"),
    ],
)
def test_outbox_diagnostics_are_classified_without_exposing_raw_message(raw, code):
    result = safe_outbox_diagnostic(raw=raw, attempts=3)
    assert result["code"] == code
    assert raw not in str(result)


def setup():
    session = AsyncMock()
    manager = MagicMock()
    manager.__aenter__ = AsyncMock(return_value=session)
    manager.__aexit__ = AsyncMock(return_value=False)
    return OperationalFailureGateway(SimpleNamespace(session=lambda: manager)), session


@pytest.mark.asyncio
async def test_filters_use_bound_parameters_and_response_has_no_raw_data():
    gateway, session = setup()
    now = datetime.now(timezone.utc)
    row = {"source": "journal", "id": "failure", "entity_id": "entry", "related_id": None,
           "state": "analyzed", "occurred_at": now, "updated_at": None, "attempts": None,
           "raw": '{"code":"provider_timeout","message":"secret","attempts":1}', "code": None}
    session.scalar.return_value = 1
    session.execute.return_value = MagicMock()
    session.execute.return_value.mappings.return_value.all.return_value = [row]
    response = await gateway.list_failures(source="journal", state="analyzed", entity_id="entry' OR 1=1", since=now, until=now, limit=5, offset=10)
    assert response["total"] == 1 and response["offset"] == 10
    assert "raw" not in response["failures"][0]
    assert "secret" not in str(response)
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "entry' OR 1=1" in query.params.values()
    assert "entry' OR 1=1" not in str(query)
    assert "ORDER BY" in str(query)
    assert 5 in query.params.values() and 10 in query.params.values()
    assert "secret text" not in str(response)


@pytest.mark.asyncio
async def test_detail_binds_both_source_and_id():
    gateway, session = setup()
    session.execute.return_value = MagicMock()
    session.execute.return_value.mappings.return_value.one_or_none.return_value = None
    assert await gateway.detail("journal", "missing") is None
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "journal" in query.params.values() and "missing" in query.params.values()


@pytest.mark.asyncio
async def test_latest_active_failure_is_correlated_by_ingestion_id():
    gateway, session = setup()
    now = datetime.now(timezone.utc)
    row = {
        "source": "outbox",
        "id": "event-id",
        "entity_id": "event-id",
        "related_id": "ingestion-id",
        "state": "FAILED",
        "occurred_at": now,
        "updated_at": now,
        "attempts": 3,
        "raw": "Error loading SSO token: token has expired",
        "code": "event_delivery_failed",
    }
    session.execute.return_value = MagicMock()
    session.execute.return_value.mappings.return_value.all.return_value = [row]

    result = await gateway.latest_active_for_ingestions(("ingestion-id",))

    assert result["ingestion-id"]["source"] == "outbox"
    assert result["ingestion-id"]["code"] == "aws_credentials_unavailable"
    assert "token has expired" not in str(result)
    query = session.execute.call_args.args[0].compile(
        dialect=postgresql.dialect()
    )
    assert any(
        value == "ingestion-id"
        or isinstance(value, list) and "ingestion-id" in value
        for value in query.params.values()
    )
    assert "FAILED" in query.params.values()
