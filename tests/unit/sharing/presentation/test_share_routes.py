from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.modules.sharing.application import ProfessionalActivityPage
from src.modules.sharing.bootstrap import (
    get_assign_professional_activities,
    get_complete_professional_activity,
    get_list_professional_activities,
)
from src.modules.sharing.domain.entities import ProfessionalActivity
from src.modules.sharing.domain.value_objects import ActivityKind, ActivityStatus
from src.modules.sharing.presentation.routes import get_share_gateway, share_router
from src.modules.auth.bootstrap.fast_api_services import get_fast_api_auth_service
from src.modules.auth.presentation.services.fast_api_auth_service import FastAPIAuthService
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.public.user_id import UserId
from src.modules.sharing.domain import ShareUnavailable, ShareIneligible
from sqlalchemy.exc import SQLAlchemyError

ID = "01M5JMVN3F84AME64TB69Y5CPF"
BASE = f"/journal/context-analyses/{ID}/shares"
HEADERS = {"Authorization": "Bearer owner-token"}
TOKEN = "a" * 43


def setup():
    gateway = SimpleNamespace(create=AsyncMock(return_value={"token": TOKEN}),
        list_shares=AsyncMock(return_value={"shares": []}), revoke=AsyncMock(return_value={"state": "revoked"}),
        resolve=AsyncMock(return_value={"result": {"summary": "Síntese"}}))
    activity_use_case = SimpleNamespace(execute=AsyncMock(return_value=(ProfessionalActivity(
        id=ID, share_id=ID, user_id="owner", kind=ActivityKind.GUIDED_REFLECTION,
        title="Observar escolhas", description="Escreva sobre uma escolha possível.",
        status=ActivityStatus.PENDING, created_at=datetime(2026, 11, 9, tzinfo=timezone.utc),
    ),)))
    listed_activity = activity_use_case.execute.return_value[0]
    list_use_case = SimpleNamespace(execute=AsyncMock(return_value=ProfessionalActivityPage(
        activities=(listed_activity,), total=1, limit=8, offset=0,
    )))
    complete_use_case = SimpleNamespace(execute=AsyncMock(return_value=ProfessionalActivity(
        id=ID, share_id=ID, user_id="owner", kind=ActivityKind.GUIDED_REFLECTION,
        title="Observar escolhas", description="Escreva sobre uma escolha possível.",
        status=ActivityStatus.COMPLETED, created_at=datetime(2026, 11, 9, tzinfo=timezone.utc),
        completed_at=datetime(2026, 11, 10, tzinfo=timezone.utc),
    )))
    activity_use_case.list_use_case = list_use_case
    activity_use_case.complete_use_case = complete_use_case
    app = FastAPI()
    app.include_router(share_router)
    service = FastAPIAuthService(SimpleNamespace(authenticate_request=AsyncMock(return_value=AuthenticatedPrincipal(UserId("owner"), UserRole.USER))))
    app.dependency_overrides[get_fast_api_auth_service] = lambda: service
    app.dependency_overrides[get_share_gateway] = lambda: gateway
    app.dependency_overrides[get_assign_professional_activities] = lambda: activity_use_case
    app.dependency_overrides[get_list_professional_activities] = lambda: list_use_case
    app.dependency_overrides[get_complete_professional_activity] = lambda: complete_use_case
    return TestClient(app), gateway, activity_use_case


def test_creation_requires_explicit_confirmation_and_uses_owner():
    client, gateway, _ = setup()
    for body in [{}, {"confirmed": False}, {"confirmed": True, "user_id": "other"}]:
        assert client.post(BASE, headers=HEADERS, json=body).status_code == 422
    gateway.create.assert_not_awaited()
    response = client.post(BASE, headers=HEADERS, json={"confirmed": True})
    assert response.status_code == 201
    assert response.headers["Cache-Control"] == "no-store"
    gateway.create.assert_awaited_once_with(ID, "owner", include_journals=False)


def test_creation_forwards_explicit_journal_authorization():
    client, gateway, _ = setup()
    response = client.post(BASE, headers=HEADERS, json={"confirmed": True, "include_journals": True})
    assert response.status_code == 201
    gateway.create.assert_awaited_once_with(ID, "owner", include_journals=True)


def test_management_requires_auth_and_revoke_is_owner_scoped():
    client, gateway, _ = setup()
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
    client, gateway, _ = setup()
    response = client.post("/shared/context-analysis/resolve", json={"token": TOKEN})
    assert response.status_code == 200
    assert response.headers["Referrer-Policy"] == "no-referrer"
    gateway.resolve.assert_awaited_once_with(TOKEN)
    for body in [{}, {"token": "short"}, {"token": "x" * 44}, {"token": "/" * 43}]:
        assert client.post("/shared/context-analysis/resolve", json=body).status_code == 422


@pytest.mark.parametrize("error,status", [(ShareUnavailable, 404), (ShareIneligible, 409), (SQLAlchemyError, 503)])
def test_errors_do_not_expose_raw_details(error, status):
    client, gateway, _ = setup()
    gateway.create.side_effect = error("private journal and credentials")
    response = client.post(BASE, headers=HEADERS, json={"confirmed": True})
    assert response.status_code == status
    assert "private" not in response.text
    assert response.headers["Cache-Control"] == "no-store"


def test_invalid_expired_revoked_token_have_same_generic_response():
    client, gateway, _ = setup()
    gateway.resolve.side_effect = ShareUnavailable()
    response = client.post("/shared/context-analysis/resolve", json={"token": TOKEN})
    assert response.status_code == 404
    assert "token_hash" not in response.text


def test_professional_assigns_guided_reflection_with_share_token():
    client, _, use_case = setup()
    response = client.post("/shared/professional-activities", json={
        "token": TOKEN,
        "activities": [{
            "kind": "guided_reflection",
            "title": " Observar escolhas ",
            "description": " Escreva sobre uma escolha possível. ",
            "due_date": None,
        }],
    })

    assert response.status_code == 201
    assert response.json()["count"] == 1
    assert response.json()["activities"][0]["kind"] == "guided_reflection"
    command = use_case.execute.await_args.args[0]
    assert command.token == TOKEN
    assert command.activities[0].title == "Observar escolhas"
    assert command.activities[0].description == "Escreva sobre uma escolha possível."
    assert response.headers["Cache-Control"] == "no-store"


def test_professional_activity_validates_token_and_content_before_use_case():
    client, _, use_case = setup()
    for body in [
        {"token": "short", "activities": [{"kind": "activity", "title": "Título", "description": "Descrição suficiente"}]},
        {"token": TOKEN, "activities": []},
        {"token": TOKEN, "activities": [{"kind": "unknown", "title": "Título", "description": "Descrição suficiente"}]},
        {"token": TOKEN, "activities": [{"kind": "activity", "title": "x", "description": "curta"}]},
    ]:
        assert client.post("/shared/professional-activities", json=body).status_code == 422
    use_case.execute.assert_not_awaited()


def test_user_lists_own_activities_with_status_and_pagination():
    client, _, use_case = setup()

    response = client.get(
        "/sharing/professional-activities?status=pending&limit=8&offset=0",
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["activities"][0]["status"] == "pending"
    query = use_case.list_use_case.execute.await_args.args[0]
    assert query.user_id == "owner"
    assert query.status is ActivityStatus.PENDING
    assert query.limit == 8
    assert query.offset == 0
    assert response.headers["Cache-Control"] == "no-store"


def test_user_completes_only_an_owned_activity_and_endpoint_is_authenticated():
    client, _, use_case = setup()
    path = f"/sharing/professional-activities/{ID}/complete"

    assert client.patch(path).status_code in (401, 403)
    response = client.patch(path, headers=HEADERS)

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["completed_at"] is not None
    use_case.complete_use_case.execute.assert_awaited_once_with(ID, "owner")
