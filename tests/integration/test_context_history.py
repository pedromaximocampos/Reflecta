from src.modules.journal.public.context_analysis import ContextPeriod
from zoneinfo import ZoneInfo
"""Opt-in real PostgreSQL + HTTP check. All fixture writes are rolled back.

CONTEXT_TEST_DATABASE_URL=postgresql+asyncpg://... DEBUG=false python -m pytest tests/integration/test_context_history.py
The target must have the project's migrations applied. No real AI requests.
"""
import os
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
import ulid
from fastapi import FastAPI
from sqlalchemy import insert, update, select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import UserModel
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.public.user_id import UserId
from src.modules.ai_processing.application.contextual_analysis import AnalyzeContext
from src.modules.journal.infrastructure.persistence.postgresql.context_gateway import ContextGateway
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel as Entry
from src.modules.journal.presentation.routes import (
    journal_router, get_current_user, get_context_gateway, get_context_case,
)

pytestmark = [pytest.mark.asyncio, pytest.mark.skipif(
    not os.getenv("CONTEXT_TEST_DATABASE_URL"), reason="Opt-in PostgreSQL integration test")]


async def test_explicit_analysis_history_pagination_owner_isolation_and_deleted_sources():
    engine = create_async_engine(os.environ["CONTEXT_TEST_DATABASE_URL"])
    owner, other = str(ulid.new()), str(ulid.new())
    now = datetime.now(timezone.utc)
    start = now.astimezone(ZoneInfo("America/Sao_Paulo")).date()
    period = {"start_date": start.isoformat(), "end_date": (start + timedelta(days=6)).isoformat()}
    result = {"summary": "Síntese fictícia", "recurring_patterns": ["Padrão fictício"],
              "changes_over_time": [], "reflection_questions": []}
    provider = SimpleNamespace(respond=AsyncMock(return_value=result))
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()

            @asynccontextmanager
            async def session_scope():
                async with AsyncSession(bind=connection, expire_on_commit=False,
                                        join_transaction_mode="create_savepoint") as session:
                    try:
                        yield session
                        await session.commit()
                    except BaseException:
                        await session.rollback()
                        raise

            gateway = ContextGateway(SimpleNamespace(session=session_scope))
            app = FastAPI()
            app.include_router(journal_router)
            app.dependency_overrides[get_current_user] = lambda: AuthenticatedPrincipal(UserId(owner), UserRole.USER)
            app.dependency_overrides[get_context_gateway] = lambda: gateway
            app.dependency_overrides[get_context_case] = lambda: AnalyzeContext(gateway, provider)
            try:
                async with session_scope() as session:
                    await session.execute(insert(UserModel), [{
                        "id": user_id, "username": "context-test-" + user_id,
                        "email": user_id + "@context-test.invalid", "name": "Context Test",
                        "date_of_birth": date(2000, 1, 1), "created_at": now,
                        "is_email_verified": False, "role": UserRole.USER,
                    } for user_id in (owner, other)])
                ids = [str(ulid.new()) for _ in range(8)]
                lower, upper = ContextPeriod(**period).bounds()
                async with session_scope() as session:
                    # Entries outside the local seven-day bounds and deleted entries
                    # cannot turn an ineligible four-entry interval into an eligible one.
                    for timestamp, deleted in [(lower - timedelta(microseconds=1), False), (upper, False), (now, True)]:
                        await session.execute(insert(Entry).values(id=str(ulid.new()), user_id=owner,
                            content_text="Não incluir na análise", status="deleted" if deleted else "pending_analysis",
                            created_at=timestamp, deleted_at=now if deleted else None))
                    await session.execute(insert(Entry).values(id=str(ulid.new()), user_id=other,
                        content_text="Entrada privada de outra conta", status="pending_analysis", created_at=lower))

                async def add_entry(index):
                    async with session_scope() as session:
                        await session.execute(insert(Entry).values(id=ids[index], user_id=owner,
                            content_text=f"Reflexão fictícia {index}", status="pending_analysis",
                            created_at=lower if index == 0 else upper - timedelta(microseconds=1) if index == 4 else now + timedelta(seconds=index)))

                for index in range(4):
                    await add_entry(index)
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                    path = "/journal/context-analysis"
                    response = await client.get(path, params=period)
                    assert response.json()["eligible"] is False
                    assert (await client.post(path, json=period)).status_code == 409
                    provider.respond.assert_not_awaited()
                    await add_entry(4)
                    assert (await client.get(path, params=period)).json()["eligible"] is True
                    assert (await client.get(path + "/history")).json()["total"] == 0
                    provider.respond.assert_not_awaited()
                    first = await client.post(path, json=period)
                    assert first.status_code == 200, first.text
                    first = first.json()
                    assert first["period"]["start_date"] == period["start_date"]
                    assert set(first["entry_ids"]) == set(ids[:5])
                    assert len(provider.respond.call_args.kwargs["input_data"]["entries"]) == 5
                    assert (await client.post(path, json=period)).json()["id"] == first["id"]
                    assert provider.respond.await_count == 1
                    await add_entry(5)
                    assert (await client.get(path, params=period)).json()["analysis"] is None
                    assert (await client.get(path + "/history")).json()["total"] == 1
                    assert provider.respond.await_count == 1  # saving + reading never generates
                    second = await client.post(path, json=period)
                    assert second.status_code == 200, second.text
                    second = second.json()
                    assert second["id"] != first["id"]
                    page1 = (await client.get(path + "/history?limit=1&offset=0")).json()
                    page2 = (await client.get(path + "/history?limit=1&offset=1")).json()
                    assert page1["total"] == 2
                    assert page1["analyses"][0]["id"] == second["id"]
                    assert page2["analyses"][0]["id"] == first["id"]
                    assert page2["analyses"][0]["result"] == result
                    async with session_scope() as session:
                        await session.execute(update(Entry).where(Entry.id == ids[0]).values(
                            status="deleted", deleted_at=now + timedelta(minutes=1)))
                    history = (await client.get(path + "/history")).json()["analyses"]
                    assert history[0]["available"] is False  # both results used all entries in the period
                    assert history[1]["available"] is False
                    assert history[1]["result"] is None and history[1]["entry_ids"] == []
                    app.dependency_overrides[get_current_user] = lambda: AuthenticatedPrincipal(UserId(other), UserRole.USER)
                    assert (await client.get(path + "/history")).json()["analyses"] == []
                    assert (await client.get(path, params=period)).json()["entry_count"] == 1
                    assert (await client.post(path, json=period)).status_code == 409
                    del app.dependency_overrides[get_current_user]
                    assert (await client.get(path + "/history")).status_code in (401, 403)
                    assert provider.respond.await_count == 2
            finally:
                await transaction.rollback()
        # The test must leave no fixture users (nor cascade-owned entries/results).
        async with engine.connect() as connection:
            assert await connection.scalar(select(func.count()).select_from(UserModel).where(
                UserModel.id.in_([owner, other]))) == 0
    finally:
        await engine.dispose()
