from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.modules.catalog.application.exceptions import WorkCoverStorageError
from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.domain.ports.repositories.iwork_repository import (
    WorkCatalogRecord,
)
from src.modules.catalog.domain.value_objects.catalog_status import CatalogStatus
from src.modules.catalog.public.analysis_recommendation_work_catalog import (
    AnalysisRecommendationWorkCatalog,
)
from src.modules.catalog.public.analysis_featured_work_catalog import (
    AnalysisFeaturedWorkCatalog,
)
from src.modules.catalog.public.author_id import AuthorId
from src.modules.catalog.public.work_id import WorkId


class _Uow:
    def __init__(self, records=(), *, passages=(), themes=()):
        self.work_repository = AsyncMock()
        self.work_repository.list_works.return_value = list(records)
        self.passage_repository = AsyncMock()
        self.passage_repository.list_passages.return_value = SimpleNamespace(
            passages=tuple(passages),
            total=len(passages),
        )
        self.theme_repository = AsyncMock()
        self.theme_repository.list_themes.return_value = list(themes)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


def _record(
    work_id: str,
    *,
    active_passage_count: int,
    cover_object_key: str | None = None,
) -> WorkCatalogRecord:
    now = datetime(2026, 11, 4, tzinfo=timezone.utc)
    return WorkCatalogRecord(
        work=Work(
            id=WorkId(work_id),
            slug=f"slug-{work_id}",
            title=f"Obra {work_id}",
            synopsis=f"Sinopse {work_id}",
            work_type="book",
            language="pt-BR",
            status=(
                CatalogStatus.ACTIVE
                if active_passage_count
                else CatalogStatus.INACTIVE
            ),
            created_at=now,
            cover_object_key=cover_object_key,
        ),
        author=Author(
            id=AuthorId(f"author-{work_id}"),
            name=f"Autor {work_id}",
            normalized_name=f"autor-{work_id}",
            description="",
            created_at=now,
        ),
        passage_count=active_passage_count,
        active_passage_count=active_passage_count,
        inactive_passage_count=0,
    )


@pytest.mark.asyncio
async def test_find_by_ids_preserves_requested_order_and_resolves_cover():
    first = _record("work-1", active_passage_count=2)
    second = _record(
        "work-2",
        active_passage_count=3,
        cover_object_key="works/work-2/cover/cover.webp",
    )
    storage = AsyncMock()
    storage.create_read_url.return_value = "https://signed.test/cover.webp"
    catalog = AnalysisRecommendationWorkCatalog(_Uow((first, second)), storage)

    works = await catalog.find_by_ids(("work-2", "work-1"))

    assert tuple(work.work_id for work in works) == ("work-2", "work-1")
    assert works[0].cover_image_url == "https://signed.test/cover.webp"
    assert works[0].active_passage_count == 3
    assert works[0].work_type == "book"
    assert works[0].language == "pt-BR"
    assert works[0].author_description == ""
    storage.create_read_url.assert_awaited_once_with(
        object_key="works/work-2/cover/cover.webp"
    )


@pytest.mark.asyncio
async def test_list_active_filters_inactive_works_before_pagination():
    records = (
        _record("work-1", active_passage_count=2),
        _record("work-2", active_passage_count=0),
        _record("work-3", active_passage_count=1),
    )
    catalog = AnalysisRecommendationWorkCatalog(_Uow(records), AsyncMock())

    page = await catalog.list_active(limit=1, offset=1)

    assert page.total == 2
    assert tuple(work.work_id for work in page.works) == ("work-3",)


@pytest.mark.asyncio
async def test_cover_failure_keeps_catalog_recommendation_available():
    record = _record(
        "work-1",
        active_passage_count=2,
        cover_object_key="works/work-1/cover/cover.webp",
    )
    storage = AsyncMock()
    storage.create_read_url.side_effect = WorkCoverStorageError(
        "create_read_url"
    )
    catalog = AnalysisRecommendationWorkCatalog(_Uow((record,)), storage)

    page = await catalog.list_active(limit=5, offset=0)

    assert page.works[0].cover_image_url is None


@pytest.mark.parametrize(
    ("limit", "offset"),
    [(0, 0), (25, 0), (5, -1)],
)
@pytest.mark.asyncio
async def test_list_active_rejects_invalid_pagination(limit: int, offset: int):
    catalog = AnalysisRecommendationWorkCatalog(_Uow(), AsyncMock())

    with pytest.raises(ValueError):
        await catalog.list_active(limit=limit, offset=offset)


@pytest.mark.asyncio
async def test_daily_feature_uses_active_work_passage_and_top_themes():
    first = _record("work-1", active_passage_count=2)
    second = _record("work-2", active_passage_count=1)
    passages = (
        SimpleNamespace(
            id=SimpleNamespace(value="passage-1"),
            short_text="Trecho principal",
            paraphrase="Leitura possível",
            locator="p. 12",
            reflective_value=.95,
            priority=0,
            themes=(
                SimpleNamespace(
                    theme_id=SimpleNamespace(value="theme-1"), confidence=.92,
                ),
            ),
        ),
    )
    themes = (
        SimpleNamespace(
            id=SimpleNamespace(value="theme-1"),
            label="O que posso controlar",
            color="#3F5B46",
            is_active=True,
        ),
    )
    catalog = AnalysisFeaturedWorkCatalog(
        _Uow((first, second), passages=passages, themes=themes),
        AsyncMock(),
    )

    featured = await catalog.get_for_day(1)

    assert featured is not None
    assert featured.work_id == "work-1"
    assert featured.passage.short_text == "Trecho principal"
    assert featured.themes[0].label == "O que posso controlar"


@pytest.mark.asyncio
async def test_daily_feature_is_empty_without_active_work():
    catalog = AnalysisFeaturedWorkCatalog(
        _Uow((_record("work-1", active_passage_count=0),)),
        AsyncMock(),
    )

    assert await catalog.get_for_day(1) is None


@pytest.mark.asyncio
async def test_daily_feature_rotates_between_high_quality_passages():
    record = _record("work-1", active_passage_count=2)
    theme = SimpleNamespace(
        id=SimpleNamespace(value="theme-1"),
        label="O que posso controlar",
        color="#3F5B46",
        is_active=True,
    )
    relevance = SimpleNamespace(
        theme_id=SimpleNamespace(value="theme-1"), confidence=.9,
    )
    passages = tuple(
        SimpleNamespace(
            id=SimpleNamespace(value=f"passage-{index}"),
            short_text=f"Trecho {index}",
            paraphrase=f"Paráfrase {index}",
            locator=f"p. {index}",
            reflective_value=value,
            priority=0,
            themes=(relevance,),
        )
        for index, value in ((1, .95), (2, .9))
    )
    catalog = AnalysisFeaturedWorkCatalog(
        _Uow((record,), passages=passages, themes=(theme,)),
        AsyncMock(),
    )

    first_day = await catalog.get_for_day(1)
    second_day = await catalog.get_for_day(2)

    assert first_day.passage.short_text == "Trecho 1"
    assert second_day.passage.short_text == "Trecho 2"
