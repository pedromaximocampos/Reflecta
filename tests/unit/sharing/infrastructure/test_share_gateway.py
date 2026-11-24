from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import pytest
from src.modules.journal.public.context_share import (
    ContextAnalysisDescriptor,
    JournalShareSourceIneligible,
    JournalShareSourceUnavailable,
    ShareableContextAnalysis,
)
from src.modules.sharing.domain import ShareIneligible, ShareUnavailable
from src.modules.sharing.infrastructure.persistence.postgresql.share_gateway import (
    ContextShareGateway,
    token_digest,
)

NOW = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
RESULT = {"summary": "Síntese", "recurring_patterns": [], "changes_over_time": [], "reflection_questions": []}


def setup():
    session = AsyncMock()
    session.add = MagicMock()
    manager = MagicMock()
    manager.__aenter__ = AsyncMock(return_value=session)
    manager.__aexit__ = AsyncMock(return_value=False)
    source = ShareableContextAnalysis(
        period={"start_date": "2026-10-20", "end_date": "2026-10-26", "timezone": "America/Sao_Paulo"},
        created_at=NOW,
        entry_count=5,
        result=RESULT,
        entries=[],
    )
    journal = SimpleNamespace(
        prepare_share=AsyncMock(return_value=source),
        ensure_available=AsyncMock(),
        describe_owned=AsyncMock(),
        describe_owned_many=AsyncMock(return_value={}),
    )
    gateway = ContextShareGateway(
        SimpleNamespace(session=lambda: manager),
        journal=journal,
        token_secret="unit-test-share-secret",
        clock=lambda: NOW,
    )
    return gateway, session, journal, source


@pytest.mark.asyncio
async def test_created_link_is_72_hours_and_only_hash_is_persisted():
    gateway, session, journal, _ = setup()
    result = await gateway.create("analysis", "owner")
    journal.prepare_share.assert_awaited_once_with(
        "analysis", "owner", include_journals=False
    )
    model = session.add.call_args.args[0]
    assert len(result["token"]) == 43
    assert model.token_hash == token_digest(result["token"]) != result["token"]
    assert model.expires_at == NOW + timedelta(hours=72)
    assert model.snapshot["result"] == RESULT
    assert set(model.snapshot) == {"schema_version", "period", "created_at", "entry_count", "result", "entries"}
    assert model.snapshot["schema_version"] == 2
    assert model.snapshot["entries"] == []
    assert "entry_ids" not in model.snapshot and "user_id" not in model.snapshot
    assert result["includes_journals"] is False


@pytest.mark.asyncio
async def test_journals_are_snapshotted_only_after_explicit_authorization():
    gateway, session, journal, source = setup()
    entry = {"entry_date": "2026-10-20", "title": "Dia difícil", "content_text": "Texto autorizado", "analysis": None}
    journal.prepare_share.return_value = ShareableContextAnalysis(
        period=source.period,
        created_at=source.created_at,
        entry_count=source.entry_count,
        result=source.result,
        entries=[entry],
    )

    result = await gateway.create("analysis", "owner", include_journals=True)

    journal.prepare_share.assert_awaited_once_with(
        "analysis", "owner", include_journals=True
    )
    model = session.add.call_args.args[0]
    assert model.snapshot["entries"] == [entry]
    assert result["includes_journals"] is True


@pytest.mark.asyncio
async def test_foreign_analysis_cannot_be_shared():
    gateway, session, journal, _ = setup()
    journal.prepare_share.side_effect = JournalShareSourceUnavailable()
    with pytest.raises(ShareUnavailable):
        await gateway.create("foreign-analysis", "owner")
    session.add.assert_not_called()


@pytest.mark.asyncio
async def test_deleted_sources_prevent_sharing():
    gateway, session, journal, _ = setup()
    journal.prepare_share.side_effect = JournalShareSourceIneligible()
    with pytest.raises(ShareIneligible):
        await gateway.create("analysis", "owner")
    session.add.assert_not_called()


def test_expiration_boundary_and_revocation_metadata():
    gateway, _, _, _ = setup()
    share = SimpleNamespace(id="share", created_at=NOW, expires_at=NOW + timedelta(days=3), revoked_at=None)
    assert gateway.metadata(share, share.expires_at)["state"] == "expired"
    assert gateway.metadata(share, share.expires_at - timedelta(microseconds=1))["state"] == "active"
    share.revoked_at = NOW
    assert gateway.metadata(share, NOW)["state"] == "revoked"


@pytest.mark.asyncio
async def test_owner_history_is_filtered_paginated_and_contains_analysis_context():
    gateway, session, journal, _ = setup()
    share = SimpleNamespace(
        id="share", analysis_id="analysis", created_at=NOW,
        expires_at=NOW + timedelta(days=3), revoked_at=None, snapshot={},
        token_hash="legacy-token-hash",
    )
    session.scalar.return_value = 1
    result = MagicMock()
    result.scalars.return_value.all.return_value = [share]
    session.execute.return_value = result
    journal.describe_owned_many.return_value = {
        "analysis": ContextAnalysisDescriptor(
            analysis_id="analysis",
            created_at=NOW,
            period={"start_date": "2026-10-20", "end_date": "2026-10-26", "timezone": "America/Sao_Paulo"},
            entry_count=5,
            summary="Síntese",
        )
    }

    page = await gateway.list_owner_shares(
        "owner", state="active", limit=5, offset=10,
    )

    assert page["total"] == 1
    assert page["limit"] == 5 and page["offset"] == 10
    assert page["shares"][0]["analysis_id"] == "analysis"
    assert page["shares"][0]["summary"] == "Síntese"
    assert page["shares"][0]["state"] == "active"
    assert "token" not in page["shares"][0]


@pytest.mark.asyncio
async def test_rotating_legacy_token_makes_active_link_recoverable():
    gateway, session, journal, _ = setup()
    share = SimpleNamespace(
        id="01TESTSHARE000000000000000",
        analysis_id="analysis",
        user_id="owner",
        created_at=NOW,
        expires_at=NOW + timedelta(days=3),
        revoked_at=None,
        snapshot={},
        token_hash="legacy-token-hash",
    )
    session.scalar.return_value = share

    rotated = await gateway.rotate_token("analysis", share.id, "owner")

    journal.describe_owned.assert_awaited_once_with("analysis", "owner")
    assert len(rotated["token"]) == 43
    assert share.token_hash == token_digest(rotated["token"])
    assert gateway.owner_metadata(share, NOW)["token"] == rotated["token"]
