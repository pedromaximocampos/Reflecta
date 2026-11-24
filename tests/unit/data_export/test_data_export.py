import base64
import json
from datetime import datetime, timezone
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock
from zipfile import ZipFile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.modules.auth.bootstrap.fast_api_services import get_fast_api_auth_service
from src.modules.auth.presentation.services.fast_api_auth_service import FastAPIAuthService
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.public.data_export import AccountDataExport, ExportedAvatar
from src.modules.auth.public.user_id import UserId
from src.modules.data_export.application import (
    ExportUserData,
    UserDataExportPackage,
    render_json_export,
    render_zip_export,
)
from src.modules.data_export.bootstrap import get_export_user_data
from src.modules.data_export.presentation.routes import data_export_router
from src.modules.journal.public.data_export import JournalDataExport
from src.modules.sharing.public.data_export import SharingDataExport


NOW = datetime(2026, 11, 20, 15, 30, tzinfo=timezone.utc)


class FixedClock:
    def now(self) -> datetime:
        return NOW


def package() -> UserDataExportPackage:
    return UserDataExportPackage(
        generated_at=NOW,
        account=AccountDataExport(
            profile={"id": "user-id", "email": "ana@example.com"},
            avatar=ExportedAvatar(
                filename="foto-perfil.webp",
                content_type="image/webp",
                content=b"avatar-bytes",
            ),
        ),
        journal=JournalDataExport(
            entries=({"id": "entry-id", "content_text": "Minha reflexão"},),
            context_analyses=({"id": "context-id", "result": {"summary": "Síntese"}},),
        ),
        sharing=SharingDataExport(
            shares=({"id": "share-id", "status": "active"},),
            professional_activities=({"id": "activity-id", "title": "Observar"},),
        ),
    )


@pytest.mark.asyncio
async def test_use_case_orchestrates_owned_export_data() -> None:
    account = SimpleNamespace(export_account=AsyncMock(return_value=package().account))
    journal = SimpleNamespace(export_journal=AsyncMock(return_value=package().journal))
    sharing = SimpleNamespace(export_sharing=AsyncMock(return_value=package().sharing))
    use_case = ExportUserData(
        account=account,
        journal=journal,
        sharing=sharing,
        clock=FixedClock(),  # type: ignore[arg-type]
    )

    result = await use_case.execute("user-id")

    assert result.generated_at == NOW
    account.export_account.assert_awaited_once_with("user-id")
    journal.export_journal.assert_awaited_once_with("user-id")
    sharing.export_sharing.assert_awaited_once_with(
        "user-id",
        generated_at=NOW,
    )


def test_json_is_self_contained_and_zip_has_human_readable_files() -> None:
    exported = package()
    document = json.loads(render_json_export(exported))

    assert document["account"]["email"] == "ana@example.com"
    assert base64.b64decode(document["account"]["avatar"]["content"]) == b"avatar-bytes"
    assert document["journal"]["entries"][0]["content_text"] == "Minha reflexão"

    with ZipFile(BytesIO(render_zip_export(exported))) as archive:
        names = set(archive.namelist())
        assert {
            "LEIA-ME.txt",
            "manifest.json",
            "perfil.json",
            "reflexoes.json",
            "analises-contextuais.json",
            "compartilhamentos.json",
            "orientacoes.json",
            "foto-perfil.webp",
        } <= names
        assert archive.read("foto-perfil.webp") == b"avatar-bytes"
        assert "password" not in archive.read("perfil.json").decode("utf-8").lower()


def client_for(exported: UserDataExportPackage) -> tuple[TestClient, AsyncMock]:
    execute = AsyncMock(return_value=exported)
    app = FastAPI()
    app.include_router(data_export_router)
    auth = FastAPIAuthService(
        SimpleNamespace(
            authenticate_request=AsyncMock(
                return_value=AuthenticatedPrincipal(UserId("user-id"), UserRole.USER)
            )
        )
    )
    app.dependency_overrides[get_fast_api_auth_service] = lambda: auth
    app.dependency_overrides[get_export_user_data] = lambda: SimpleNamespace(
        execute=execute
    )
    return TestClient(app), execute


def test_endpoint_exports_zip_and_json_with_private_download_headers() -> None:
    client, execute = client_for(package())
    headers = {"Authorization": "Bearer owner-token"}

    zipped = client.get("/account/data-export?format=zip", headers=headers)
    assert zipped.status_code == 200
    assert zipped.headers["Content-Type"] == "application/zip"
    assert zipped.headers["Cache-Control"] == "no-store"
    assert "reflecta-meus-dados-2026-11-20.zip" in zipped.headers["Content-Disposition"]

    json_response = client.get("/account/data-export?format=json", headers=headers)
    assert json_response.status_code == 200
    assert json_response.headers["Content-Type"].startswith("application/json")
    assert json_response.json()["manifest"]["schema_version"] == "1.0"
    assert execute.await_count == 2


def test_endpoint_requires_authentication_and_rejects_unknown_format() -> None:
    client, execute = client_for(package())

    assert client.get("/account/data-export").status_code in (401, 403)
    response = client.get(
        "/account/data-export?format=csv",
        headers={"Authorization": "Bearer owner-token"},
    )
    assert response.status_code == 422
    execute.assert_not_awaited()
