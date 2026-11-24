from datetime import date, datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.journal.infrastructure.persistence.postgresql.journal_share_snapshot import JournalShareSnapshotBuilder


@pytest.mark.asyncio
async def test_snapshot_contains_public_curated_analysis_without_internal_ids():
    session = AsyncMock()
    entry = SimpleNamespace(
        id="private-entry-id",
        entry_date=date(2026, 10, 20),
        created_at=datetime(2026, 10, 20, tzinfo=timezone.utc),
        title="Escolhas",
        content_text="Tenho tentado controlar todas as possibilidades.",
    )
    entries_result = MagicMock()
    entries_result.scalars.return_value.all.return_value = [entry]

    sentence = SimpleNamespace(id="private-sentence-id")
    theme = SimpleNamespace(theme_id="private-theme-id")
    sentence_result = MagicMock()
    sentence_result.all.return_value = [(sentence, theme)]

    passage = SimpleNamespace(
        sentence_id=sentence.id,
        reason="A passagem amplia o ponto central da reflexão.",
        payload_snapshot={
            "short_text": "Escolha sua resposta diante do que acontece.",
            "paraphrase": "É possível escolher como responder.",
            "locator": "p. 10",
            "work": {"title": "Manual", "author_name": "Epicteto"},
            "theme_matches": [{"theme_id": theme.theme_id}],
        },
    )
    passage_result = MagicMock()
    passage_result.scalars.return_value.all.return_value = [passage]
    session.execute.side_effect = [entries_result, sentence_result, passage_result]
    session.scalar.return_value = SimpleNamespace(
        id="private-analysis-id",
        main_message="Nem tudo depende de você.",
        summary="Resumo interno.",
        content_meta={
            "themes": [{"id": theme.theme_id, "label": "O que Posso Controlar", "color": "#3C6E47"}],
            "user_theme_selection": {"theme_ids": [theme.theme_id]},
        },
    )

    snapshots = await JournalShareSnapshotBuilder().build(
        session,
        SimpleNamespace(entry_ids=[entry.id]),
        "owner-id",
    )

    assert snapshots[0]["analysis"]["conclusion"] == "Nem tudo depende de você."
    assert snapshots[0]["analysis"]["themes"] == [{"label": "O que Posso Controlar", "color": "#3C6E47"}]
    assert snapshots[0]["analysis"]["passages"][0]["work_title"] == "Manual"
    serialized = str(snapshots)
    for private_id in [entry.id, sentence.id, theme.theme_id, "private-analysis-id", "owner-id"]:
        assert private_id not in serialized
