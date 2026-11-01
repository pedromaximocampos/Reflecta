"""Share-link HTTP + PostgreSQL check. All fixture writes roll back; no AI calls."""
import hashlib
import os
from contextlib import asynccontextmanager
from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
import httpx
import pytest
import ulid
from sqlalchemy import insert, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.main.server.fast_api.server import create_fast_api_app
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.public.user_id import UserId
from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import UserModel
from src.modules.auth.bootstrap.fast_api_services import get_fast_api_auth_service
from src.modules.auth.presentation.services.fast_api_auth_service import FastAPIAuthService
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel as Entry
from src.modules.journal.infrastructure.persistence.postgresql.models.context_analysis_model import ContextAnalysisModel as Analysis
from src.modules.journal.infrastructure.persistence.postgresql.models.context_share_model import ContextShareModel as Share
from src.modules.journal.infrastructure.persistence.postgresql.share_gateway import ContextShareGateway
from src.modules.journal.presentation.share_routes import get_share_gateway

pytestmark = [pytest.mark.asyncio, pytest.mark.skipif(not os.getenv('SHARING_TEST_DATABASE_URL'), reason='Opt-in PostgreSQL integration test')]


async def test_share_confirmation_token_privacy_expiry_revocation_and_source_deletion():
    engine = create_async_engine(os.environ['SHARING_TEST_DATABASE_URL'])
    owner, other, analysis_id, legacy_id = [str(ulid.new()) for _ in range(4)]
    ids = [str(ulid.new()) for _ in range(5)]
    now = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
    clock = [now]
    secret = 'PRIVATE-PROFILE-JOURNAL-TEXT'
    result = {'summary': 'Síntese autorizada', 'recurring_patterns': ['Padrão observado'], 'changes_over_time': [], 'reflection_questions': ['O que mudou?']}
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            @asynccontextmanager
            async def scope():
                async with AsyncSession(bind=connection, expire_on_commit=False, join_transaction_mode='create_savepoint') as session:
                    try:
                        yield session
                        await session.commit()
                    except BaseException:
                        await session.rollback()
                        raise
            gateway = ContextShareGateway(SimpleNamespace(session=scope), clock=lambda: clock[0])
            app = create_fast_api_app()
            actor = AuthenticatedPrincipal(UserId(owner), UserRole.USER)
            async def authenticate(token):
                return actor
            app.dependency_overrides[get_fast_api_auth_service] = lambda: FastAPIAuthService(SimpleNamespace(authenticate_request=AsyncMock(side_effect=authenticate)))
            app.dependency_overrides[get_share_gateway] = lambda: gateway
            try:
                async with scope() as session:
                    for user_id in [owner, other]:
                        await session.execute(insert(UserModel).values(id=user_id, username='share-test-' + user_id,
                            email=user_id + '@share-test.invalid', name=secret, date_of_birth=date(2000, 1, 1),
                            created_at=now, is_email_verified=False, role=UserRole.USER))
                    for entry_id in ids:
                        await session.execute(insert(Entry).values(id=entry_id, user_id=owner, content_text=secret,
                            title=secret, status='analyzed', created_at=now))
                    for analysis, start, end in [(analysis_id, date(2026, 10, 23), date(2026, 10, 29)), (legacy_id, None, None)]:
                        await session.execute(insert(Analysis).values(id=analysis, user_id=owner, fingerprint=analysis,
                            entry_ids=ids, result=result, created_at=now, period_start=start, period_end=end))
                base = f'/journal/context-analyses/{analysis_id}/shares'
                resolve = '/shared/context-analysis/resolve'
                headers = {'Authorization': 'Bearer fictitious-owner-token'}
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
                    assert (await client.post(base, headers=headers, json={'confirmed': False})).status_code == 400
                    assert (await client.post(base, json={'confirmed': True})).status_code in (401, 403)
                    assert (await client.post(f'/journal/context-analyses/{legacy_id}/shares', headers=headers, json={'confirmed': True})).status_code == 409
                    created = await client.post(base, headers=headers, json={'confirmed': True})
                    assert created.status_code == 201, created.text
                    first = created.json()
                    assert datetime.fromisoformat(first['expires_at']) - now == timedelta(hours=72)
                    async with scope() as session:
                        row = await session.scalar(select(Share).where(Share.id == first['id']))
                        assert row.token_hash == hashlib.sha256(first['token'].encode()).hexdigest()
                        assert first['token'] not in str(row.snapshot)
                        assert set(row.snapshot) == {'period', 'created_at', 'entry_count', 'result'}
                    metadata = await client.get(base, headers=headers)
                    assert 'token' not in metadata.text and 'snapshot' not in metadata.text
                    public = await client.post(resolve, json={'token': first['token']})
                    assert public.status_code == 200, public.text
                    shared = public.json()
                    assert shared['result'] == result
                    assert set(shared) == {'period', 'created_at', 'entry_count', 'result', 'expires_at'}
                    assert shared['entry_count'] == 5
                    for private in [secret, owner, other, analysis_id, *ids]:
                        assert private not in public.text
                    assert public.headers['cache-control'] == 'no-store'
                    assert public.headers['referrer-policy'] == 'no-referrer'
                    assert (await client.post(resolve, json={'token': 'z' * 43})).status_code == 404
                    clock[0] = now + timedelta(days=3) - timedelta(microseconds=1)
                    assert (await client.post(resolve, json={'token': first['token']})).status_code == 200
                    clock[0] = now + timedelta(days=3)
                    expired = await client.post(resolve, json={'token': first['token']})
                    assert expired.status_code == 404 and expired.headers['cache-control'] == 'no-store'
                    clock[0] = now
                    second = (await client.post(base, headers=headers, json={'confirmed': True})).json()
                    assert second['token'] != first['token']
                    actor = AuthenticatedPrincipal(UserId(other), UserRole.ADMIN)  # admin role does not bypass ownership
                    assert (await client.get(base, headers=headers)).status_code == 404
                    assert (await client.post(base, headers=headers, json={'confirmed': True})).status_code == 404
                    assert (await client.delete(base + '/' + second['id'], headers=headers)).status_code == 404
                    actor = AuthenticatedPrincipal(UserId(owner), UserRole.USER)
                    revoked = await client.delete(base + '/' + second['id'], headers=headers)
                    assert revoked.json()['state'] == 'revoked'
                    assert (await client.delete(base + '/' + second['id'], headers=headers)).json()['revoked_at'] == revoked.json()['revoked_at']
                    assert (await client.post(resolve, json={'token': second['token']})).status_code == 404
                    third = (await client.post(base, headers=headers, json={'confirmed': True})).json()
                    async with scope() as session:
                        await session.execute(update(Entry).where(Entry.id == ids[0]).values(status='deleted', deleted_at=now))
                    assert (await client.post(resolve, json={'token': third['token']})).status_code == 404
                    assert (await client.post(base, headers=headers, json={'confirmed': True})).status_code == 409
                    async with scope() as session:
                        await session.execute(update(Entry).where(Entry.id == ids[0]).values(status='analyzed', deleted_at=None))
                        await session.execute(update(UserModel).where(UserModel.id == owner).values(deleted_at=now))
                    assert (await client.post(resolve, json={'token': third['token']})).status_code == 404
            finally:
                await transaction.rollback()
        async with engine.connect() as connection:
            assert await connection.scalar(select(func.count()).select_from(UserModel).where(UserModel.id.in_([owner, other]))) == 0
    finally:
        await engine.dispose()
