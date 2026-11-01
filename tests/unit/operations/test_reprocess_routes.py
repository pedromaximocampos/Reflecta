from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from sqlalchemy.exc import SQLAlchemyError
from src.modules.auth.public import UserRole
from src.modules.operations.presentation.routes import get_reprocess_gateway
from src.modules.journal.public.analysis import AnalysisConflictError, UserReprocessLimitError
from src.modules.journal.domain.exceptions.journal_exceptions import JournalEntryNotFoundError
from tests.unit.operations.test_failure_routes import setup, HEADERS, BASE

FAILURE_ID = "01M5JMVN3F84AME64TB69Y5CPF"


def client_for(role=UserRole.ADMIN):
    client, _ = setup(role)
    gateway = SimpleNamespace(admin_reprocess=AsyncMock(return_value={"entry_id": "entry", "status": "pending_analysis", "already_pending": False}))
    client.app.dependency_overrides[get_reprocess_gateway] = lambda: gateway
    return client, gateway


def test_admin_submission_returns_confirmation_and_uses_authenticated_admin():
    client, gateway = client_for()
    response = client.post(BASE + f"/journal/{FAILURE_ID}/reprocess", headers=HEADERS)
    assert response.status_code == 202
    assert response.json()["status"] == "pending_analysis"
    assert gateway.admin_reprocess.call_args.args == (FAILURE_ID, "actor")


def test_non_admin_cannot_bypass_limit_through_admin_endpoint():
    client, gateway = client_for(UserRole.USER)
    assert client.post(BASE + f"/journal/{FAILURE_ID}/reprocess", headers=HEADERS).status_code == 403
    gateway.admin_reprocess.assert_not_awaited()


@pytest.mark.parametrize("error,status", [(AnalysisConflictError, 409), (JournalEntryNotFoundError, 404), (ValueError, 400), (SQLAlchemyError, 503)])
def test_admin_errors_are_safe(error, status):
    client, gateway = client_for()
    gateway.admin_reprocess.side_effect = error()
    response = client.post(BASE + f"/journal/{FAILURE_ID}/reprocess", headers=HEADERS)
    assert response.status_code == status


def test_invalid_ids_and_missing_auth_are_rejected():
    client, gateway = client_for()
    assert client.post(BASE + "/journal/bad/reprocess", headers=HEADERS).status_code == 422
    assert client.post(BASE + f"/journal/{FAILURE_ID}/reprocess").status_code in (401, 403)
    gateway.admin_reprocess.assert_not_awaited()


def test_owner_endpoint_returns_policy_and_generic_limit_error():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from src.modules.journal.presentation.routes import journal_router, get_analysis_gateway, get_current_user
    app = FastAPI()
    app.include_router(journal_router)
    gateway = SimpleNamespace(submit=AsyncMock(return_value={"status": "pending_analysis", "reprocess": {"user_used": 1}}))
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(user_id=SimpleNamespace(value="owner"))
    app.dependency_overrides[get_analysis_gateway] = lambda: gateway
    client = TestClient(app)
    path = f"/journal/entries/{FAILURE_ID}/analysis"
    response = client.post(path, json={"expected_revision": "2026-10-27T12:00:00Z"})
    assert response.status_code == 202 and response.json()["reprocess"]["user_used"] == 1
    assert gateway.submit.call_args.args == (FAILURE_ID, "owner")
    assert gateway.submit.call_args.kwargs["expected_revision"].tzinfo is not None
    gateway.submit.side_effect = UserReprocessLimitError()
    response = client.post(path)
    assert response.status_code == 403
    assert "administrador" in response.text
    assert "provider" not in response.text and "analysis_error" not in response.text
    for body in [{"user_reprocess_count": 0}, {"actor_role": "ADMIN"}, {"expected_revision": "bad"}]:
        assert client.post(path, json=body).status_code == 422
