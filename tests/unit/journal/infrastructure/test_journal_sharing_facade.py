from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.journal.infrastructure.persistence.postgresql.journal_sharing_facade import (
    PostgresJournalSharingFacade,
)
from src.modules.journal.public.context_share import (
    JournalShareSourceIneligible,
    JournalShareSourceUnavailable,
)


NOW = datetime(2026, 10, 29, 12, tzinfo=timezone.utc)
RESULT = {
    "summary": "Síntese",
    "recurring_patterns": [],
    "changes_over_time": [],
    "reflection_questions": [],
}


def setup_facade():
    session = AsyncMock()
    manager = MagicMock()
    manager.__aenter__ = AsyncMock(return_value=session)
    manager.__aexit__ = AsyncMock(return_value=False)
    snapshot_builder = SimpleNamespace(build=AsyncMock(return_value=[]))
    facade = PostgresJournalSharingFacade(
        SimpleNamespace(session=lambda: manager),
        snapshot_builder=snapshot_builder,
    )
    analysis = SimpleNamespace(
        id="analysis",
        user_id="owner",
        entry_ids=[f"entry-{index}" for index in range(5)],
        period_start=date(2026, 10, 20),
        period_end=date(2026, 10, 26),
        created_at=NOW,
        result=RESULT,
    )
    return facade, session, snapshot_builder, analysis


@pytest.mark.asyncio
async def test_prepare_share_exposes_only_the_public_contract():
    facade, session, snapshot_builder, analysis = setup_facade()
    session.scalar.side_effect = [analysis, 5]

    source = await facade.prepare_share(
        "analysis",
        "owner",
        include_journals=False,
    )

    assert source.period == {
        "start_date": "2026-10-20",
        "end_date": "2026-10-26",
        "timezone": "America/Sao_Paulo",
    }
    assert source.entry_count == 5
    assert source.result == RESULT
    assert source.entries == []
    snapshot_builder.build.assert_not_awaited()


@pytest.mark.asyncio
async def test_prepare_share_builds_journal_snapshot_only_when_authorized():
    facade, session, snapshot_builder, analysis = setup_facade()
    session.scalar.side_effect = [analysis, 5]
    entries = [
        {
            "entry_date": "2026-10-20",
            "title": "Reflexão",
            "content_text": "Texto autorizado",
            "analysis": None,
        }
    ]
    snapshot_builder.build.return_value = entries

    source = await facade.prepare_share(
        "analysis",
        "owner",
        include_journals=True,
    )

    snapshot_builder.build.assert_awaited_once_with(session, analysis, "owner")
    assert source.entries == entries


@pytest.mark.asyncio
async def test_foreign_or_deleted_owner_analysis_is_unavailable():
    facade, session, _, _ = setup_facade()
    session.scalar.return_value = None

    with pytest.raises(JournalShareSourceUnavailable):
        await facade.prepare_share(
            "analysis",
            "another-user",
            include_journals=False,
        )


@pytest.mark.asyncio
async def test_missing_source_entry_makes_analysis_ineligible():
    facade, session, _, analysis = setup_facade()
    session.scalar.side_effect = [analysis, 4]

    with pytest.raises(JournalShareSourceIneligible):
        await facade.prepare_share(
            "analysis",
            "owner",
            include_journals=False,
        )

