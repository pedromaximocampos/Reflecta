from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.public.user_id import UserId
from src.modules.auth.presentation.services.fast_api_auth_service import FastAPIAuthService
from src.modules.auth.bootstrap.fast_api_services import get_fast_api_auth_service
from src.modules.journal.presentation.routes import journal_router
from src.modules.operations.presentation.routes import get_failure_gateway

ENTRY_ID = "01M5JMVN3F84AME64TB69Y5CPF"


def setup_client(role=UserRole.ADMIN):
    gateway = SimpleNamespace(list_failures=AsyncMock(return_value={"failures": [], "total": 0}))
    app = FastAPI()
    app.include_router(journal_router)
    auth = FastAPIAuthService(SimpleNamespace(authenticate_request=AsyncMock(
        return_value=AuthenticatedPrincipal(UserId("admin"), role))))
    app.dependency_overrides[get_fast_api_auth_service] = lambda: auth
    app.dependency_overrides[get_failure_gateway] = lambda: gateway
    return TestClient(app), gateway


def test_legacy_failure_route_is_admin_only_and_can_trace_any_entry():
    client, gateway = setup_client()
    response = client.get(f"/journal/entries/{ENTRY_ID}/analysis/failures?limit=5", headers={"Authorization": "Bearer admin"})
    assert response.status_code == 200
    gateway.list_failures.assert_awaited_once_with(source="journal", entity_id=ENTRY_ID, limit=5)


def test_legacy_failure_route_validates_limits_and_id():
    client, gateway = setup_client()
    for path in [f"{ENTRY_ID}/analysis/failures?limit=0", f"{ENTRY_ID}/analysis/failures?limit=101", "bad-id/analysis/failures"]:
        assert client.get("/journal/entries/" + path, headers={"Authorization": "Bearer admin"}).status_code == 422
    gateway.list_failures.assert_not_awaited()


def test_legacy_failure_route_refuses_normal_user_even_for_own_entry():
    client, gateway = setup_client(UserRole.USER)
    response = client.get(f"/journal/entries/{ENTRY_ID}/analysis/failures", headers={"Authorization": "Bearer owner"})
    assert response.status_code == 403
    assert "provider_timeout" not in response.text
    gateway.list_failures.assert_not_awaited()


def test_legacy_failure_route_requires_authentication():
    client, gateway = setup_client()
    assert client.get(f"/journal/entries/{ENTRY_ID}/analysis/failures").status_code in (401, 403)
    gateway.list_failures.assert_not_awaited()
