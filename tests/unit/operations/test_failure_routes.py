from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.public.user_id import UserId
from src.modules.auth.presentation.services.fast_api_auth_service import FastAPIAuthService
from src.modules.auth.bootstrap.fast_api_services import get_fast_api_auth_service
from src.modules.operations.presentation.routes import operations_router, get_failure_gateway

HEADERS = {"Authorization": "Bearer test"}
BASE = "/admin/operational-failures"


def setup(role=UserRole.ADMIN):
    app = FastAPI()
    app.include_router(operations_router)
    gateway = SimpleNamespace(list_failures=AsyncMock(return_value={"failures": [], "total": 0, "limit": 20, "offset": 0}),
                              detail=AsyncMock(return_value={"code": "provider_timeout"}))
    auth = FastAPIAuthService(SimpleNamespace(authenticate_request=AsyncMock(
        return_value=AuthenticatedPrincipal(UserId("actor"), role))))
    app.dependency_overrides[get_fast_api_auth_service] = lambda: auth
    app.dependency_overrides[get_failure_gateway] = lambda: gateway
    return TestClient(app), gateway


@pytest.mark.parametrize("path", [BASE, BASE + "/journal/id"])
def test_regular_users_cannot_read_operational_reasons(path):
    client, gateway = setup(UserRole.USER)
    response = client.get(path, headers=HEADERS)
    assert response.status_code == 403
    gateway.list_failures.assert_not_awaited()
    gateway.detail.assert_not_awaited()


@pytest.mark.parametrize("path", [BASE, BASE + "/journal/id"])
def test_authentication_required(path):
    client, gateway = setup()
    assert client.get(path).status_code in (401, 403)
    gateway.list_failures.assert_not_awaited()
    gateway.detail.assert_not_awaited()


def test_admin_filters_pagination_and_detail():
    client, gateway = setup()
    response = client.get(BASE, params={"source": "journal", "state": "analysis_failed", "entity_id": "entry", "limit": 5, "offset": 10}, headers=HEADERS)
    assert response.status_code == 200
    gateway.list_failures.assert_awaited_once_with(source="journal", state="analysis_failed", entity_id="entry", since=None, until=None, limit=5, offset=10)
    assert client.get(BASE + "/inbox/consumer:event", headers=HEADERS).status_code == 200
    gateway.detail.assert_awaited_once_with("inbox", "consumer:event")


@pytest.mark.parametrize("params", [{"source": "invalid"}, {"state": "invalid"}, {"limit": 0}, {"limit": 101},
    {"offset": -1}, {"entity_id": "x" * 129}, {"since": "bad-date"}, {"since": "2026-10-27T00:00:00"},
    {"since": "2026-10-28T00:00:00Z", "until": "2026-10-27T00:00:00Z"}])
def test_filters_are_validated(params):
    client, gateway = setup()
    assert client.get(BASE, params=params, headers=HEADERS).status_code == 422
    gateway.list_failures.assert_not_awaited()


def test_detail_not_found_and_database_failure_are_safe():
    client, gateway = setup()
    gateway.detail.return_value = None
    assert client.get(BASE + "/journal/missing", headers=HEADERS).status_code == 404
    gateway.list_failures.side_effect = SQLAlchemyError("secret credentials and journal")
    response = client.get(BASE, headers=HEADERS)
    assert response.status_code == 503
    assert "secret" not in response.text
    gateway.detail.side_effect = SQLAlchemyError("secret credentials and journal")
    response = client.get(BASE + "/journal/id", headers=HEADERS)
    assert response.status_code == 503
    assert "secret" not in response.text
