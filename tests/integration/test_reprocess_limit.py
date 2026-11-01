"""Opt-in PostgreSQL tests. No provider calls. Fictitious records are cleaned up."""
import asyncio
import os
from contextlib import asynccontextmanager
from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
import ulid
from fastapi import FastAPI
from sqlalchemy import insert, select, func, delete, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.main.server.fast_api.fast_api_exception_handler import add_exception_handlers
from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import UserModel
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.public.user_id import UserId
from src.modules.auth.presentation.services.fast_api_auth_service import FastAPIAuthService
from src.modules.auth.bootstrap.fast_api_services import get_fast_api_auth_service
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel as Entry
from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel as Analysis
from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_reprocess_model import AnalysisReprocessModel as Audit
from src.modules.journal.infrastructure.persistence.postgresql.analysis_gateway import JournalAnalysisGateway
from src.modules.journal.public.analysis import AnalysisFailure, AnalysisConflictError
from src.modules.journal.presentation.routes import journal_router, get_analysis_gateway
from src.modules.operations.infrastructure.failure_gateway import OperationalFailureGateway
from src.modules.operations.presentation.routes import operations_router, get_failure_gateway, get_reprocess_gateway
from src.modules.ai_processing.worker import LOCK_ID

pytestmark = [pytest.mark.asyncio, pytest.mark.skipif(
    not os.getenv("REPROCESS_TEST_DATABASE_URL"), reason="Opt-in PostgreSQL integration test")]


async def seed(session, owner, entry_id, *, used=0):
    now = datetime.now(timezone.utc)
    await session.execute(insert(UserModel).values(id=owner, username="retry-test-" + owner,
        email=owner + "@retry-test.invalid", name="Reprocess Test", date_of_birth=date(2000, 1, 1),
        created_at=now, is_email_verified=False, role=UserRole.USER))
    await session.execute(insert(Entry).values(id=entry_id, user_id=owner, content_text="Texto fictício de teste.",
        status="pending_analysis", created_at=now, user_reprocess_count=used))


async def mark_failure(gateway, entry_id, owner):
    snapshot = await gateway.read(entry_id, owner)
    await gateway.mark_failed(snapshot, now=datetime.now(timezone.utc),
        failure=AnalysisFailure("provider_timeout", "private provider detail", 2))


async def test_http_three_user_requests_then_admin_only_and_auditing():
    engine = create_async_engine(os.environ["REPROCESS_TEST_DATABASE_URL"])
    owner, admin, other, entry_id = [str(ulid.new()) for _ in range(4)]
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            @asynccontextmanager
            async def scope():
                async with AsyncSession(bind=connection, expire_on_commit=False, join_transaction_mode="create_savepoint") as session:
                    try:
                        yield session
                        await session.commit()
                    except BaseException:
                        await session.rollback()
                        raise
            gateway = JournalAnalysisGateway(SimpleNamespace(session=scope))
            operations = OperationalFailureGateway(SimpleNamespace(session=scope))
            app = FastAPI()
            app.include_router(journal_router)
            app.include_router(operations_router)
            add_exception_handlers(app)
            actor = AuthenticatedPrincipal(UserId(owner), UserRole.USER)
            async def authenticate(token):
                return actor
            app.dependency_overrides[get_fast_api_auth_service] = lambda: FastAPIAuthService(SimpleNamespace(authenticate_request=AsyncMock(side_effect=authenticate)))
            app.dependency_overrides[get_analysis_gateway] = lambda: gateway
            app.dependency_overrides[get_reprocess_gateway] = lambda: gateway
            app.dependency_overrides[get_failure_gateway] = lambda: operations
            try:
                async with scope() as session:
                    await seed(session, owner, entry_id)
                    await session.execute(insert(UserModel).values(id=admin, username="retry-admin-" + admin,
                        email=admin + "@retry-test.invalid", name="Admin Test", date_of_birth=date(2000, 1, 1),
                        created_at=datetime.now(timezone.utc), is_email_verified=False, role=UserRole.ADMIN))
                path = f"/journal/entries/{entry_id}/analysis"
                headers = {"Authorization": "Bearer test-token"}
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                    await mark_failure(gateway, entry_id, owner)  # initial run is free, including bounded provider retries
                    for number in range(1, 4):
                        status = (await client.get(path, headers=headers)).json()
                        assert status["reprocess"]["user_used"] == number - 1
                        assert status["reprocess"]["can_user_reprocess"] is True
                        assert "private provider" not in str(status)
                        body = {"expected_revision": status["reprocess"]["revision"]}
                        first = await client.post(path, json=body, headers=headers)
                        assert first.status_code == 202, first.text
                        assert first.json()["reprocess"]["user_used"] == number
                        duplicate = await client.post(path, json=body, headers=headers)
                        assert duplicate.status_code == 202
                        assert duplicate.json()["reprocess"]["user_used"] == number
                        await mark_failure(gateway, entry_id, owner)
                        # A delayed request for the previous failed revision must not charge again.
                        delayed = await client.post(path, json=body, headers=headers)
                        assert delayed.status_code == (409 if number < 3 else 403)
                    blocked = (await client.get(path, headers=headers)).json()
                    assert blocked["reprocess"]["requires_admin"] is True
                    assert blocked["reprocess"]["user_remaining"] == 0
                    assert (await client.post(path, json={"expected_revision": blocked["reprocess"]["revision"]}, headers=headers)).status_code == 403
                    assert (await client.get(path + "/failures", headers=headers)).status_code == 403
                    actor = AuthenticatedPrincipal(UserId(other), UserRole.USER)
                    assert (await client.post(path, json={"expected_revision": blocked["reprocess"]["revision"]}, headers=headers)).status_code == 404
                    async with scope() as session:
                        latest = await session.scalar(gateway._latest_failure(entry_id))
                    admin_path = f"/admin/operational-failures/journal/{latest}/reprocess"
                    assert (await client.post(admin_path, headers=headers)).status_code == 403
                    actor = AuthenticatedPrincipal(UserId(admin), UserRole.ADMIN)
                    preview = (await client.get(f"/admin/operational-failures/journal/{latest}", headers=headers)).json()
                    assert preview["can_admin_reprocess"] is True
                    assert preview["reprocess"]["user_used"] == 3
                    settings = {"model": "gpt-6-luna", "timeout_seconds": 60.0,
                                "max_output_tokens": 12000, "reasoning_effort": "low"}
                    accepted = await client.post(admin_path, headers=headers, json=settings)
                    assert accepted.status_code == 202, accepted.text
                    assert accepted.json()["reprocess"]["user_used"] == 3
                    assert (await client.post(admin_path, headers=headers)).json()["already_pending"] is True
                    async with scope() as session:
                        rows = (await session.execute(select(Audit).where(Audit.entry_id == entry_id).order_by(Audit.requested_at))).scalars().all()
                        assert [row.actor_role for row in rows] == ["USER", "USER", "USER", "ADMIN"]
                        assert [row.user_attempt_number for row in rows] == [1, 2, 3, None]
                        assert rows[-1].processing_settings == settings
                        assert all(row.processing_settings is None for row in rows[:-1])
                    snapshot = await gateway.read(entry_id, owner)
                    assert snapshot.processing_settings == settings
                    await gateway.save(snapshot, analysis_id=str(ulid.new()), summary="Resumo fictício", main_message="Mensagem fictícia",
                        metadata={}, now=datetime.now(timezone.utc), sentences=())
                    async with scope() as session:
                        assert await session.scalar(select(Entry.processing_settings).where(Entry.id == entry_id)) is None
                    assert (await client.post(admin_path, headers=headers)).status_code == 409
            finally:
                await transaction.rollback()
        async with engine.connect() as connection:
            assert await connection.scalar(select(func.count()).select_from(UserModel).where(UserModel.id.in_([owner, admin]))) == 0
    finally:
        await engine.dispose()


async def test_real_parallel_sessions_charge_once_and_save_only_one_result():
    engine = create_async_engine(os.environ["REPROCESS_TEST_DATABASE_URL"])
    factory = async_sessionmaker(engine, expire_on_commit=False)
    owner, entry_id = str(ulid.new()), str(ulid.new())
    @asynccontextmanager
    async def scope():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except BaseException:
                await session.rollback()
                raise
    gateway = JournalAnalysisGateway(SimpleNamespace(session=scope))
    # Hold the same advisory lock used by the worker. Committed fictitious pending
    # rows cannot be picked by a live worker or trigger any paid provider request.
    lock_connection = await engine.connect()
    try:
        await lock_connection.execute(text("SELECT pg_advisory_lock(:id)"), {"id": LOCK_ID})
        async with scope() as session:
            await seed(session, owner, entry_id, used=2)
        await mark_failure(gateway, entry_id, owner)
        status = await gateway.get_analysis(entry_id, owner)
        revision = datetime.fromisoformat(status["reprocess"]["revision"])
        replies = await asyncio.gather(*(gateway.submit(entry_id, owner, now=datetime.now(timezone.utc), expected_revision=revision) for _ in range(2)))
        assert [reply["reprocess"]["user_used"] for reply in replies] == [3, 3]
        async with scope() as session:
            assert await session.scalar(select(func.count()).select_from(Audit).where(Audit.entry_id == entry_id)) == 1
        await mark_failure(gateway, entry_id, owner)
        async with scope() as session:
            latest = await session.scalar(gateway._latest_failure(entry_id))
        # Owner is also used as the authenticated admin identifier here; role
        # enforcement is exercised by the HTTP test above, gateway concurrency here.
        replies = await asyncio.gather(*(gateway.admin_reprocess(latest, owner, now=datetime.now(timezone.utc)) for _ in range(2)))
        assert sorted(reply["already_pending"] for reply in replies) == [False, True]
        snapshot = await gateway.read(entry_id, owner)
        async def save_result():
            return await gateway.save(snapshot, analysis_id=str(ulid.new()), summary="Resumo fictício", main_message="Mensagem fictícia",
                metadata={}, now=datetime.now(timezone.utc), sentences=())
        results = await asyncio.gather(save_result(), save_result(), return_exceptions=True)
        assert sum(isinstance(result, AnalysisConflictError) for result in results) == 1
        async with scope() as session:
            assert await session.scalar(select(func.count()).select_from(Analysis).where(Analysis.journal_entry_id == entry_id, Analysis.status == "completed")) == 1
            assert await session.scalar(select(func.count()).select_from(Audit).where(Audit.entry_id == entry_id)) == 2
            assert await session.scalar(select(Entry.user_reprocess_count).where(Entry.id == entry_id)) == 3
    finally:
        try:
            # Narrow cleanup: only this test's generated fixture account.
            async with scope() as session:
                await session.execute(delete(UserModel).where(UserModel.id == owner))
            async with scope() as session:
                assert await session.scalar(select(func.count()).select_from(UserModel).where(UserModel.id == owner)) == 0
        finally:
            await lock_connection.execute(text("SELECT pg_advisory_unlock(:id)"), {"id": LOCK_ID})
            await lock_connection.close()
            await engine.dispose()
