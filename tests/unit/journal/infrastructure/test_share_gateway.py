from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import pytest
from src.modules.journal.infrastructure.persistence.postgresql.share_gateway import ContextShareGateway, ShareUnavailable, ShareIneligible, token_digest

NOW = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
RESULT = {"summary": "Síntese", "recurring_patterns": [], "changes_over_time": [], "reflection_questions": []}


def setup():
    session = AsyncMock()
    session.add = MagicMock()
    manager = MagicMock()
    manager.__aenter__ = AsyncMock(return_value=session)
    manager.__aexit__ = AsyncMock(return_value=False)
    analysis = SimpleNamespace(user_id="owner", entry_ids=[str(i) for i in range(5)],
        period_start=date(2026, 10, 20), period_end=date(2026, 10, 26), created_at=NOW, result=RESULT)
    return ContextShareGateway(SimpleNamespace(session=lambda: manager), clock=lambda: NOW), session, analysis


@pytest.mark.asyncio
async def test_created_link_is_72_hours_and_only_hash_is_persisted():
    gateway, session, analysis = setup()
    session.scalar.side_effect = [analysis, 5]
    result = await gateway.create("analysis", "owner")
    model = session.add.call_args.args[0]
    assert len(result["token"]) == 43
    assert model.token_hash == token_digest(result["token"]) != result["token"]
    assert model.expires_at == NOW + timedelta(hours=72)
    assert model.snapshot["result"] == RESULT
    assert set(model.snapshot) == {"period", "created_at", "entry_count", "result"}
    assert "entry_ids" not in model.snapshot and "user_id" not in model.snapshot


@pytest.mark.asyncio
async def test_foreign_analysis_cannot_be_shared():
    gateway, session, _ = setup()
    session.scalar.return_value = None
    with pytest.raises(ShareUnavailable):
        await gateway.create("foreign-analysis", "owner")
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_deleted_sources_prevent_sharing():
    gateway, session, analysis = setup()
    session.scalar.side_effect = [analysis, 4]
    with pytest.raises(ShareIneligible):
        await gateway.create("analysis", "owner")
    session.add.assert_not_called()


def test_expiration_boundary_and_revocation_metadata():
    gateway, _, _ = setup()
    share = SimpleNamespace(id="share", created_at=NOW, expires_at=NOW + timedelta(days=3), revoked_at=None)
    assert gateway.metadata(share, share.expires_at)["state"] == "expired"
    assert gateway.metadata(share, share.expires_at - timedelta(microseconds=1))["state"] == "active"
    share.revoked_at = NOW
    assert gateway.metadata(share, NOW)["state"] == "revoked"
