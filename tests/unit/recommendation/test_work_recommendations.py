from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.modules.catalog.public import (
    RecommendationWork,
    RecommendationWorkPage,
)
from src.modules.recommendation.application import (
    ExploreWorks,
    GetHomeDashboard,
    GetRecommendationWork,
    RecommendWorks,
)


@pytest.mark.asyncio
async def test_home_dashboard_composes_entries_metrics_and_recommendations():
    journal = SimpleNamespace(
        home_snapshot=AsyncMock(return_value={
            "summary": {
                "metrics": {"total_reflections": 4},
                "recurring_themes": [{
                    "theme_id": "theme-1",
                    "label": "Controle",
                    "reflection_count": 2,
                }],
            },
            "entries": [{"id": "entry-1"}],
            "entries_has_next": False,
            "entry_limit": 4,
            "entry_offset": 0,
        })
    )
    recommendations = SimpleNamespace(
        execute_from_affinities=AsyncMock(return_value={
            "recommendations": [{"work_id": "work-1"}],
            "total": 1,
            "limit": 2,
            "offset": 0,
        })
    )

    result = await GetHomeDashboard(journal, recommendations).execute("owner")

    assert result["entries"] == [{"id": "entry-1"}]
    assert result["summary"]["metrics"]["total_reflections"] == 4
    assert result["recommendations"]["recommendations"] == [{"work_id": "work-1"}]
    journal.home_snapshot.assert_awaited_once_with(
        "owner", entry_limit=4, entry_offset=0,
    )
    recommendations.execute_from_affinities.assert_awaited_once_with(
        ({
            "theme_id": "theme-1",
            "label": "Controle",
            "reflection_count": 2,
        },),
        limit=2,
        offset=0,
    )


@pytest.mark.asyncio
async def test_recommendations_rank_distinct_works_from_theme_affinity():
    journal = SimpleNamespace(theme_affinities=AsyncMock(return_value=(
        {"theme_id": "control", "slug": "control", "label": "Controle", "color": "#123456", "reflection_count": 3},
        {"theme_id": "courage", "slug": "courage", "label": "Coragem", "color": "#654321", "reflection_count": 1},
    )))
    catalog = SimpleNamespace(find_active_by_themes=AsyncMock(return_value=(
        SimpleNamespace(work_id="work-a", work_title="Manual", author_name="Autor A", passage_id="p1", matched_theme_id="control", matched_theme_confidence=.9, short_text="Trecho A"),
        SimpleNamespace(work_id="work-a", work_title="Manual", author_name="Autor A", passage_id="p2", matched_theme_id="control", matched_theme_confidence=.8, short_text="Trecho B"),
        SimpleNamespace(work_id="work-b", work_title="Ensaios", author_name="Autor B", passage_id="p3", matched_theme_id="courage", matched_theme_confidence=1, short_text="Trecho C"),
    )))
    works = SimpleNamespace(find_by_ids=AsyncMock(return_value=(
        RecommendationWork(
            work_id="work-a",
            title="Manual",
            author_name="Autor A",
            synopsis="Uma obra sobre a prática estoica.",
            cover_image_url="https://signed.test/manual.webp",
            active_passage_count=8,
        ),
    )))

    result = await RecommendWorks(journal, catalog, works).execute("owner", limit=1)

    assert result["total"] == 2
    assert result["recommendations"][0]["work_id"] == "work-a"
    assert result["recommendations"][0]["score"] == 2.7
    assert result["recommendations"][0]["active_passage_count"] == 8
    assert result["recommendations"][0]["cover_image_url"] == (
        "https://signed.test/manual.webp"
    )
    assert result["recommendations"][0]["synopsis"] == (
        "Uma obra sobre a prática estoica."
    )
    catalog.find_active_by_themes.assert_awaited_once_with(
        ("control", "courage"), limit_per_theme=10,
    )
    works.find_by_ids.assert_awaited_once_with(("work-a",))


@pytest.mark.asyncio
async def test_no_affinity_returns_empty_page_without_catalog_query():
    journal = SimpleNamespace(theme_affinities=AsyncMock(return_value=()))
    catalog = SimpleNamespace(find_active_by_themes=AsyncMock())
    works = SimpleNamespace(find_by_ids=AsyncMock())

    result = await RecommendWorks(journal, catalog, works).execute("owner")

    assert result["recommendations"] == []
    catalog.find_active_by_themes.assert_not_awaited()
    works.find_by_ids.assert_not_awaited()


@pytest.mark.asyncio
async def test_explore_works_serializes_active_catalog_page():
    works = SimpleNamespace(list_active=AsyncMock(return_value=(
        RecommendationWorkPage(
            works=(RecommendationWork(
                work_id="work-a",
                title="Manual",
                author_name="Autor A",
                synopsis="Sinopse",
                cover_image_url=None,
                active_passage_count=3,
                work_type="book",
                language="pt-BR",
                author_description="Sobre o autor",
            ),),
            total=7,
            limit=1,
            offset=2,
        )
    )))

    result = await ExploreWorks(works).execute(limit=1, offset=2)

    assert result == {
        "works": [{
            "work_id": "work-a",
            "title": "Manual",
            "author_name": "Autor A",
            "author_description": "Sobre o autor",
            "work_type": "book",
            "language": "pt-BR",
            "synopsis": "Sinopse",
            "cover_image_url": None,
            "active_passage_count": 3,
        }],
        "total": 7,
        "limit": 1,
        "offset": 2,
    }
    works.list_active.assert_awaited_once_with(limit=1, offset=2)


@pytest.mark.asyncio
async def test_get_recommendation_work_returns_safe_active_details():
    work = RecommendationWork(
        work_id="work-a",
        title="Manual",
        author_name="Autor A",
        author_description="Sobre o autor",
        work_type="book",
        language="pt-BR",
        synopsis="Sinopse",
        cover_image_url="https://signed.test/manual.webp",
        active_passage_count=3,
    )
    works = SimpleNamespace(find_by_ids=AsyncMock(return_value=(work,)))

    result = await GetRecommendationWork(works).execute("work-a")

    assert result == {
        "work_id": "work-a",
        "title": "Manual",
        "author_name": "Autor A",
        "author_description": "Sobre o autor",
        "work_type": "book",
        "language": "pt-BR",
        "synopsis": "Sinopse",
        "cover_image_url": "https://signed.test/manual.webp",
        "active_passage_count": 3,
    }
    works.find_by_ids.assert_awaited_once_with(("work-a",))


@pytest.mark.asyncio
async def test_get_recommendation_work_hides_inactive_work():
    inactive = RecommendationWork(
        work_id="work-a",
        title="Manual",
        author_name="Autor A",
        synopsis="Sinopse",
        cover_image_url=None,
        active_passage_count=0,
    )
    works = SimpleNamespace(find_by_ids=AsyncMock(return_value=(inactive,)))

    assert await GetRecommendationWork(works).execute("work-a") is None

