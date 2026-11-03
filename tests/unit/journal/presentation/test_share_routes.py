from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.modules.journal.presentation.share_routes import share_router, get_share_gateway
from src.modules.auth.bootstrap.fast_api_services import get_fast_api_auth_service
from src.modules.auth.presentation.services.fast_api_auth_service import FastAPIAuthService
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.public.user_id import UserId
from src.modules.journal.infrastructure.persistence.postgresql.share_gateway import ShareUnavailable, ShareIneligible
from sqlalchemy.exc import SQLAlchemyError

ID = "01M5JMVN3F84AME64TB69Y5CPF"
BASE = f"/journal/context-analyses/{ID}/shares"
HEADERS = {"Authorization": "Bearer owner-token"}
TOKEN = "a" * 43


def setup():
    gateway = SimpleNamespace(create=AsyncMock(return_value={"token": TOKEN}),
        list_shares=AsyncMock(return_value={"shares": []}), revoke=AsyncMock(return_value={"state": "revoked"}),
        resolve=AsyncMock(return_value={"result": {"summary": "Síntese"}}))
    app = FastAPI()
    app.include_router(share_router)
    service = FastAPIAuthService(SimpleNamespace(authenticate_request=AsyncMock(return_value=AuthenticatedPrincipal(UserId("owner"), UserRole.USER))))
    app.dependency_overrides[get_fast_api_auth_service] = lambda: service
    app.dependency_overrides[get_share_gateway] = lambda: gateway
    return TestClient(app), gateway


def test_creation_requires_explicit_confirmation_and_uses_owner():
    client, gateway = setup()
    for body in [{}, {"confirmed": False}, {"confirmed": True, "user_id": "other"}]:
        assert client.post(BASE, headers=HEADERS, json=body).status_code == 422
    gateway.create.assert_not_awaited()
    response = client.post(BASE, headers=HEADERS, json={"confirmed": True})
    assert response.status_code == 201
    assert response.headers["Cache-Control"] == "no-store"
    gateway.create.assert_awaited_once_with(ID, "owner")


def test_management_requires_auth_and_revoke_is_owner_scoped():
    client, gateway = setup()
    assert client.get(BASE).status_code in (401, 403)
    assert client.post(BASE, json={"confirmed": True}).status_code in (401, 403)
    assert client.delete(BASE + "/" + ID).status_code in (401, 403)
    gateway.create.assert_not_awaited()
    gateway.list_shares.assert_not_awaited()
    gateway.revoke.assert_not_awaited()
    assert client.get(BASE, headers=HEADERS).status_code == 200
    gateway.list_shares.assert_awaited_once_with(ID, "owner")
    assert client.delete(BASE + "/" + ID, headers=HEADERS).status_code == 200
    gateway.revoke.assert_awaited_once_with(ID, ID, "owner")


def test_receiver_needs_only_token_no_authentication():
    client, gateway = setup()
    response = client.post("/shared/context-analysis/resolve", json={"token": TOKEN})
    assert response.status_code == 200
    assert response.headers["Referrer-Policy"] == "no-referrer"
    gateway.resolve.assert_awaited_once_with(TOKEN)
    for body in [{}, {"token": "short"}, {"token": "x" * 44}, {"token": "/" * 43}]:
        assert client.post("/shared/context-analysis/resolve", json=body).status_code == 422


@pytest.mark.parametrize("error,status", [(ShareUnavailable, 404), (ShareIneligible, 409), (SQLAlchemyError, 503)])
def test_errors_do_not_expose_raw_details(error, status):
    client, gateway = setup()
    gateway.create.side_effect = error("private journal and credentials")
    response = client.post(BASE, headers=HEADERS, json={"confirmed": True})
    assert response.status_code == status
    assert "private" not in response.text
    assert response.headers["Cache-Control"] == "no-store"


def test_invalid_expired_revoked_token_have_same_generic_response():
    client, gateway = setup()
    gateway.resolve.side_effect = ShareUnavailable()
    response = client.post("/shared/context-analysis/resolve", json={"token": TOKEN})
    assert response.status_code == 404
    assert "token_hash" not in response.text
