from unittest.mock import AsyncMock

import pytest

from src.modules.catalog.infrastructure.persistence.neo4j.repositories.passage_repository import (
    PassageRepository,
)


def _result(*records: dict) -> AsyncMock:
    result = AsyncMock()
    result.__aiter__.return_value = iter(records)
    return result


@pytest.mark.asyncio
async def test_find_active_contextual_candidates_maps_catalog_projection() -> None:
    record = {
        "theme_rank": 0,
        "matched_theme_id": "theme-1",
        "candidate": {
            "passage_id": "passage-1",
            "theme_confidence": 0.94,
            "short_text": "A passagem literal da obra.",
            "paraphrase": "Uma paráfrase da passagem.",
            "interpretation_note": "A relação reflexiva com o tema.",
            "locator": "p. 10",
            "priority": 2,
            "start_page": 10,
            "end_page": 10,
            "work_id": "work-1",
            "work_title": "Meditações",
            "author_name": "Marco Aurélio",
        },
    }
    transaction = AsyncMock()
    transaction.run.return_value = _result(record)
    repository = PassageRepository(transaction, AsyncMock())

    candidates = await repository.find_active_contextual_candidates(
        theme_ids=("theme-1", "theme-2"),
        limit_per_theme=4,
    )

    assert len(candidates) == 1
    assert candidates[0].passage_id == "passage-1"
    assert candidates[0].matched_theme_id == "theme-1"
    assert candidates[0].matched_theme_confidence == 0.94
    assert candidates[0].work_title == "Meditações"
    assert candidates[0].author_name == "Marco Aurélio"
    assert transaction.run.await_args.kwargs == {
        "theme_ids": ["theme-1", "theme-2"],
        "limit_per_theme": 4,
    }

    query = transaction.run.await_args.args[0]
    assert "passage:Passage {status: 'ACTIVE'}" in query
    assert "is_active: true" in query
    assert "[:BELONGS_TO]" in query
    assert "[:WRITTEN_BY]" in query
    assert "[..$limit_per_theme]" in query


@pytest.mark.asyncio
async def test_find_active_contextual_candidates_skips_empty_query() -> None:
    transaction = AsyncMock()
    repository = PassageRepository(transaction, AsyncMock())

    assert (
        await repository.find_active_contextual_candidates(
            theme_ids=(),
            limit_per_theme=5,
        )
        == []
    )
    transaction.run.assert_not_awaited()

