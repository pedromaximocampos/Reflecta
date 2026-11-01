"""Opt-in real database / HTTP test, entirely rolled back and without AI calls."""
import json
import os
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
import ulid
from fastapi import FastAPI
from sqlalchemy import insert, select, func, text, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import UserModel
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.public.user_id import UserId
from src.modules.auth.presentation.services.fast_api_auth_service import FastAPIAuthService
from src.modules.auth.bootstrap.fast_api_services import get_fast_api_auth_service
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel as Entry
from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel as Analysis
from src.modules.internal_events.infrastructure.persistence.postgresql.models.outbox_model import OutboxModel as Outbox
from src.modules.operations.infrastructure.failure_gateway import OperationalFailureGateway
from src.modules.operations.presentation.routes import operations_router, get_failure_gateway
from src.modules.journal.presentation.routes import journal_router

pytestmark = [pytest.mark.asyncio, pytest.mark.skipif(
    not os.getenv("OPERATIONS_TEST_DATABASE_URL"), reason="Opt-in PostgreSQL integration test")]


async def test_admin_failures_all_sources_filters_details_and_user_diagnostic_denial():
    engine = create_async_engine(os.environ["OPERATIONS_TEST_DATABASE_URL"])
    owner, entry_id, analysis_id, legacy_id, ingestion_id, chunk_id, event_id, outbox_id = [str(ulid.new()) for _ in range(8)]
    now = datetime.now(timezone.utc)
    secret = "DO-NOT-EXPOSE-private-journal-key-payload"
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()

            @asynccontextmanager
            async def session_scope():
                async with AsyncSession(bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint") as session:
                    try:
                        yield session
                        await session.commit()
                    except BaseException:
                        await session.rollback()
                        raise

            gateway = OperationalFailureGateway(SimpleNamespace(session=session_scope))
            app = FastAPI()
            app.include_router(operations_router)
            app.include_router(journal_router)
            actor = AuthenticatedPrincipal(UserId(owner), UserRole.USER)
            async def authenticate(token):
                return actor
            auth = FastAPIAuthService(SimpleNamespace(authenticate_request=AsyncMock(side_effect=authenticate)))
            app.dependency_overrides[get_fast_api_auth_service] = lambda: auth
            app.dependency_overrides[get_failure_gateway] = lambda: gateway
            try:
                async with session_scope() as session:
                    await session.execute(insert(UserModel).values(id=owner, username="op-test-" + owner,
                        email=owner + "@op-test.invalid", name="Operations Test", date_of_birth=date(2000, 1, 1),
                        created_at=now, is_email_verified=False, role=UserRole.USER))
                    await session.execute(insert(Entry).values(id=entry_id, user_id=owner, title=secret,
                        content_text=secret, context_tags={"private": secret}, status="analysis_failed", created_at=now))
                    await session.execute(insert(Analysis), [dict(id=analysis_id, journal_entry_id=entry_id,
                        status="failed", created_at=now, analysis_error=json.dumps({"code": "provider_timeout", "message": secret, "attempts": 2})),
                        dict(id=legacy_id, journal_entry_id=entry_id, status="failed", created_at=now - timedelta(seconds=1), analysis_error=secret)])
                    await session.execute(text('''INSERT INTO catalog_schema.work_ingestions
                        (id,work_id,requested_by,s3_bucket,s3_object_key,status,attempts,created_at,finished_at,error_code,error_message)
                        VALUES (:id,:work,:owner,'test-bucket',CAST(:secret AS text),'failed',1,:now,:now,'WorkDocumentExtractionError',CAST(:secret AS text))'''),
                        {"id": ingestion_id, "work": str(ulid.new()), "owner": owner, "secret": secret, "now": now})
                    await session.execute(text('''INSERT INTO ai_processing_schema.work_ingestion_chunks
                        (id,ingestion_id,chunk_index,start_page,end_page,start_offset,end_offset,content_sha256,chunker_version,status,attempts,created_at,updated_at,error_code,error_message)
                        VALUES (:id,:ingestion,0,1,1,0,10,:hash,'test','failed',1,:now,:now,'work_passage_analysis_failed',:secret)'''),
                        {"id": chunk_id, "ingestion": ingestion_id, "hash": "0" * 64, "now": now, "secret": secret})
                    await session.execute(text('''INSERT INTO ai_processing_schema.inbox_events
                        (consumer_name,event_id,status,attempts,received_at,updated_at,error_code,error_message)
                        VALUES ('test_consumer',:event,'failed',1,:now,:now,'unexpected_error',:secret)'''),
                        {"event": event_id, "now": now, "secret": secret})
                    await session.execute(insert(Outbox).values(id=outbox_id, event_type="TEST", payload={"secret": secret, "ingestion_id": ingestion_id},
                        status="FAILED", attempts=3, event_occurred_at=now, created_at=now, failed_at=now, last_error=secret))
                headers = {"Authorization": "Bearer fictitious-token"}
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                    base = "/admin/operational-failures"
                    # Even the owner cannot access diagnostics through either URL.
                    for path in [base, base + "/journal/" + analysis_id, f"/journal/entries/{entry_id}/analysis/failures"]:
                        response = await client.get(path, headers=headers)
                        assert response.status_code == 403, response.text
                        assert secret not in response.text
                    actor = AuthenticatedPrincipal(UserId(owner), UserRole.ADMIN)
                    # Bound the query to test fixtures using the occurrence timestamp.
                    params = {"since": (now - timedelta(seconds=2)).isoformat(), "until": (now + timedelta(seconds=1)).isoformat(), "limit": 100}
                    response = await client.get(base, params=params, headers=headers)
                    assert response.status_code == 200, response.text
                    assert secret not in response.text
                    sources = {row["source"] for row in response.json()["failures"]}
                    assert sources == {"journal", "work_ingestion", "work_chunk", "inbox", "outbox"}
                    outbox_failure = next(row for row in response.json()["failures"] if row["source"] == "outbox")
                    assert outbox_failure["related_id"] == ingestion_id
                    response = await client.get(base, params={**params, "source": "journal", "entity_id": entry_id, "limit": 1}, headers=headers)
                    page = response.json()
                    assert page["total"] == 2 and len(page["failures"]) == 1
                    assert page["failures"][0]["id"] == analysis_id
                    response = await client.get(base, params={**params, "source": "journal", "entity_id": entry_id, "limit": 1, "offset": 1}, headers=headers)
                    assert response.json()["failures"][0]["code"] == "unknown_error"
                    detail = await client.get(base + "/journal/" + analysis_id, headers=headers)
                    assert detail.json()["attempts"] == 2
                    assert detail.json()["message"] == "O provedor excedeu o tempo limite da análise."
                    assert secret not in detail.text and "raw" not in detail.json()
                    assert (await client.get(base + "/inbox/test_consumer:" + event_id, headers=headers)).status_code == 200
                    assert (await client.get(base + "/journal/" + str(ulid.new()), headers=headers)).status_code == 404
                    assert (await client.get(base, params={"entity_id": "x' OR 1=1 --"}, headers=headers)).json()["total"] == 0
                    async with session_scope() as session:
                        await session.execute(update(Entry).where(Entry.id == entry_id).values(status="analyzed"))
                    recovered = await client.get(base, params={"source": "journal", "state": "analyzed", "entity_id": entry_id}, headers=headers)
                    assert recovered.json()["total"] == 2
                    legacy = await client.get(f"/journal/entries/{entry_id}/analysis/failures", headers=headers)
                    assert legacy.status_code == 200 and secret not in legacy.text
                    assert (await client.get(base)).status_code in (401, 403)
            finally:
                await transaction.rollback()
        async with engine.connect() as connection:
            assert await connection.scalar(select(func.count()).select_from(UserModel).where(UserModel.id == owner)) == 0
    finally:
        await engine.dispose()
