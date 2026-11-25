from unittest.mock import AsyncMock, Mock

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
            "reflective_value": 0.875,
            "reflective_note": "A passagem abre uma perspectiva não prescritiva.",
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
    assert candidates[0].reflective_value == 0.875
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
    assert "coalesce(passage.reflective_value, 0) DESC" in query
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


@pytest.mark.asyncio
async def test_list_passages_applies_pagination_and_returns_filtered_total() -> None:
    count_result = AsyncMock()
    count_result.single.return_value = {"total": 42}
    page_result = _result({"passage": {"passage_id": "p-1"}, "themes": []})
    transaction = AsyncMock()
    transaction.run.side_effect = [count_result, page_result]
    mapper = Mock()
    mapped = object()
    mapper.to_entity.return_value = mapped
    repository = PassageRepository(transaction, mapper)

    page = await repository.list_passages(
        work_title="meditações",
        author_name="marco",
        confidence_min=0.8,
        limit=20,
        offset=20,
    )

    assert page.passages == (mapped,)
    assert page.total == 42
    assert transaction.run.await_count == 2
    assert transaction.run.await_args.kwargs["limit"] == 20
    assert transaction.run.await_args.kwargs["offset"] == 20
    query = transaction.run.await_args.args[0]
    assert "SKIP $offset" in query
    assert "LIMIT $limit" in query
    assert "matched_relevance.confidence" in query


@pytest.mark.asyncio
async def test_count_by_status_returns_small_admin_projection() -> None:
    transaction = AsyncMock()
    transaction.run.return_value = _result(
        {"status": "ACTIVE", "total": 12},
        {"status": "PENDING_REVIEW", "total": 3},
    )
    repository = PassageRepository(transaction, Mock())

    result = await repository.count_by_status()

    assert result == {"ACTIVE": 12, "PENDING_REVIEW": 3}

