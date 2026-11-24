from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.dialects import postgresql

from src.modules.journal.infrastructure.persistence.postgresql.dashboard_gateway import (
    JournalDashboardGateway,
)


NOW = datetime(2026, 11, 4, 15, tzinfo=timezone.utc)


def setup():
    session = AsyncMock()
    manager = MagicMock()
    manager.__aenter__ = AsyncMock(return_value=session)
    manager.__aexit__ = AsyncMock(return_value=False)
    return JournalDashboardGateway(
        SimpleNamespace(session=lambda: manager),
        clock=lambda: NOW,
    ), session


@pytest.mark.asyncio
async def test_summary_uses_real_owner_data_and_counts_themes_per_reflection():
    gateway, session = setup()
    metadata = {
        "themes": [
            {"id": "theme-a", "slug": "controle", "label": "Controle", "color": "#123456"},
            {"id": "theme-b", "slug": "coragem", "label": "Coragem", "color": "#654321"},
        ]
    }
    theme_result = MagicMock()
    theme_result.all.return_value = [
        (metadata, "entry-1"),
        (metadata, "entry-2"),
        (metadata, "entry-2"),
    ]
    passage = SimpleNamespace(
        passage_id="passage-1",
        payload_snapshot={
            "short_text": "Uma passagem",
            "locator": "p. 10",
            "theme_matches": [{"theme_id": "theme-a"}],
            "work": {"id": "work-1", "title": "Manual", "author_name": "Autor"},
        },
    )
    passage_result = MagicMock()
    passage_result.all.return_value = [(passage, metadata, "theme-a")]
    session.execute.side_effect = [theme_result, passage_result]
    session.scalar.side_effect = [2, 7]

    result = await gateway.summary("owner")

    assert result["period"] == {"month": 11, "year": 2026}
    assert result["metrics"] == {
        "reflections_this_month": 2,
        "total_reflections": 7,
        "explored_themes": 2,
    }
    assert result["recurring_themes"][0]["reflection_count"] == 2
    assert result["latest_reference"]["work_title"] == "Manual"
    for call in session.scalar.call_args_list[:2]:
        query = call.args[0].compile(dialect=postgresql.dialect())
        assert "owner" in query.params.values()


@pytest.mark.asyncio
async def test_theme_affinities_respect_user_curation_overlay():
    gateway, session = setup()
    result = MagicMock()
    result.all.return_value = [({
        "themes": [
            {"id": "kept", "slug": "kept", "label": "Mantido"},
            {"id": "hidden", "slug": "hidden", "label": "Ocultado"},
        ],
        "user_theme_selection": {"theme_ids": ["kept"]},
    }, "entry-1")]
    session.execute.return_value = result

    affinities = await gateway.theme_affinities("owner")

    assert [theme["theme_id"] for theme in affinities] == ["kept"]


@pytest.mark.asyncio
async def test_theme_affinities_are_owner_scoped_ranked_and_limited():
    gateway, session = setup()
    result = MagicMock()
    result.all.return_value = [
        ({"themes": [{"id": "a", "slug": "a", "label": "A", "color": None}]}, "entry-1"),
        ({"themes": [{"id": "a", "slug": "a", "label": "A", "color": None}]}, "entry-2"),
        ({"themes": [{"id": "b", "slug": "b", "label": "B", "color": None}]}, "entry-1"),
    ]
    session.execute.return_value = result

    affinities = await gateway.theme_affinities("owner", limit=1)

    assert affinities == ({
        "theme_id": "a", "slug": "a", "label": "A",
        "color": None, "reflection_count": 2,
    },)
    query = session.execute.call_args.args[0].compile(dialect=postgresql.dialect())
    assert "owner" in query.params.values()

