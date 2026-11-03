from src.modules.journal.public.context_analysis import ContextPeriod
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from src.modules.journal.presentation.routes import get_context_analysis, submit_context_analysis
from src.modules.ai_processing.application.contextual_analysis import InsufficientHistoryError, HistoryChangedError
from src.modules.ai_processing.application.contracts import InterpretationFailedError, ProviderNotConfiguredError

USER = SimpleNamespace(user_id=SimpleNamespace(value="authenticated-owner"))


PERIOD = ContextPeriod(start_date="2026-10-20", end_date="2026-10-26")

@pytest.mark.asyncio
async def test_read_status_never_requests_generation():
    gateway = SimpleNamespace(status=AsyncMock(return_value={"eligible": True, "analysis": None}))
    assert await get_context_analysis(period=PERIOD, current_user=USER, gateway=gateway) == {"eligible": True, "analysis": None}
    gateway.status.assert_awaited_once_with("authenticated-owner", PERIOD)


@pytest.mark.asyncio
async def test_post_uses_authenticated_owner():
    case = SimpleNamespace(execute=AsyncMock(return_value={"id": "saved"}))
    assert await submit_context_analysis(period=PERIOD, current_user=USER, case=case) == {"id": "saved"}
    case.execute.assert_awaited_once_with("authenticated-owner", PERIOD)


@pytest.mark.asyncio
@pytest.mark.parametrize("error,status", [(InsufficientHistoryError, 409), (HistoryChangedError, 409),
    (InterpretationFailedError, 503), (ProviderNotConfiguredError, 503), (SQLAlchemyError, 503)])
async def test_errors_are_safe_and_retryable(error, status):
    case = SimpleNamespace(execute=AsyncMock(side_effect=error("secret input")))
    with pytest.raises(HTTPException) as caught:
        await submit_context_analysis(period=PERIOD, current_user=USER, case=case)
    assert caught.value.status_code == status
    assert "secret" not in caught.value.detail


@pytest.mark.asyncio
async def test_read_unavailability_is_safe():
    gateway = SimpleNamespace(status=AsyncMock(side_effect=SQLAlchemyError("secret db")))
    with pytest.raises(HTTPException) as caught:
        await get_context_analysis(period=PERIOD, current_user=USER, gateway=gateway)
    assert caught.value.status_code == 503
    assert "secret" not in caught.value.detail


@pytest.mark.asyncio
async def test_context_diagnostic_logs_only_allowlisted_reason(caplog):
    from src.modules.ai_processing.application.failure_reasons import FailureReason
    case = SimpleNamespace(execute=AsyncMock(side_effect=InterpretationFailedError(
        "secret journal and key", reason=FailureReason.INCOMPLETE)))
    with pytest.raises(HTTPException) as caught:
        await submit_context_analysis(period=PERIOD, current_user=USER, case=case)
    assert 'provider_incomplete_response' in caplog.text
    assert 'secret' not in caplog.text
    assert 'provider_incomplete_response' not in caught.value.detail


@pytest.mark.asyncio
async def test_history_endpoint_uses_owner_and_pagination_without_generation():
    from src.modules.journal.presentation.routes import get_context_analysis_history
    response = {"analyses": [], "total": 0, "limit": 5, "offset": 10}
    gateway = SimpleNamespace(history=AsyncMock(return_value=response))
    assert await get_context_analysis_history(limit=5, offset=10, current_user=USER, gateway=gateway) == response
    gateway.history.assert_awaited_once_with("authenticated-owner", limit=5, offset=10)


@pytest.mark.asyncio
async def test_history_unavailability_returns_safe_error():
    from src.modules.journal.presentation.routes import get_context_analysis_history
    gateway = SimpleNamespace(history=AsyncMock(side_effect=SQLAlchemyError("secret")))
    with pytest.raises(HTTPException) as caught:
        await get_context_analysis_history(limit=5, offset=0, current_user=USER, gateway=gateway)
    assert caught.value.status_code == 503
    assert "secret" not in caught.value.detail


@pytest.mark.asyncio
@pytest.mark.parametrize("query", ["limit=0", "limit=51", "offset=-1"])
async def test_history_rejects_invalid_pagination_at_http_boundary(query):
    import httpx
    from fastapi import FastAPI
    from src.modules.journal.presentation.routes import journal_router, get_context_gateway, get_current_user
    app = FastAPI()
    app.include_router(journal_router)
    gateway = SimpleNamespace(history=AsyncMock())
    app.dependency_overrides[get_current_user] = lambda: USER
    app.dependency_overrides[get_context_gateway] = lambda: gateway
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/journal/context-analysis/history?{query}")
    assert response.status_code == 422
    gateway.history.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize('period', [None, {'start_date': '2026-10-20', 'end_date': '2026-10-25'},
    {'start_date': '2026-10-20', 'end_date': '2026-10-27'},
    {'start_date': 'invalid', 'end_date': '2026-10-26'}])
async def test_period_is_required_and_validated_before_generation(period):
    import httpx
    from fastapi import FastAPI
    from src.modules.journal.presentation.routes import journal_router, get_context_case, get_context_gateway, get_current_user
    app = FastAPI()
    app.include_router(journal_router)
    case = SimpleNamespace(execute=AsyncMock())
    gateway = SimpleNamespace(status=AsyncMock())
    app.dependency_overrides[get_current_user] = lambda: USER
    app.dependency_overrides[get_context_case] = lambda: case
    app.dependency_overrides[get_context_gateway] = lambda: gateway
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
        assert (await client.post('/journal/context-analysis', json=period)).status_code == 422
        assert (await client.get('/journal/context-analysis', params=period)).status_code == 422
    case.execute.assert_not_awaited()
    gateway.status.assert_not_awaited()
