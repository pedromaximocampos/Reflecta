from unittest.mock import AsyncMock

import pytest

from src.modules.catalog.public.analysis_contextual_passage_catalog import (
    AnalysisContextualPassageCatalog,
)
from src.modules.catalog.domain.ports.repositories.ipassage_repository import (
    ContextualPassageRecord,
)
from src.modules.catalog.public.contextual_passage import (
    ContextualPassageCandidate,
)


def _candidate() -> ContextualPassageCandidate:
    return ContextualPassageCandidate(
        passage_id="passage-1",
        matched_theme_id="theme-1",
        matched_theme_confidence=0.94,
        short_text="A passagem literal da obra.",
        paraphrase="Uma paráfrase da passagem.",
        interpretation_note="A relação reflexiva com o tema.",
        locator="p. 10",
        priority=2,
        work_id="work-1",
        work_title="Meditações",
        author_name="Marco Aurélio",
        start_page=10,
        end_page=10,
    )


def _record() -> ContextualPassageRecord:
    return ContextualPassageRecord(**_candidate().model_dump())


class _Uow:
    def __init__(self, candidates=()):
        self.passage_repository = AsyncMock()
        self.passage_repository.find_active_contextual_candidates.return_value = list(
            candidates
        )
        self.entries = 0

    async def __aenter__(self):
        self.entries += 1
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


@pytest.mark.asyncio
async def test_catalog_returns_active_candidates_from_repository() -> None:
    uow = _Uow((_record(),))
    catalog = AnalysisContextualPassageCatalog(uow)

    candidates = await catalog.find_active_by_themes(
        ("theme-1", "theme-2"),
        limit_per_theme=4,
    )

    assert candidates == (_candidate(),)
    uow.passage_repository.find_active_contextual_candidates.assert_awaited_once_with(
        theme_ids=("theme-1", "theme-2"),
        limit_per_theme=4,
    )


@pytest.mark.asyncio
async def test_catalog_skips_neo4j_when_no_themes_were_selected() -> None:
    uow = _Uow()
    catalog = AnalysisContextualPassageCatalog(uow)

    assert await catalog.find_active_by_themes(()) == ()
    assert uow.entries == 0
    uow.passage_repository.find_active_contextual_candidates.assert_not_awaited()


@pytest.mark.parametrize(
    ("theme_ids", "limit_per_theme"),
    [
        (("theme-1", "theme-1"), 5),
        (("",), 5),
        (("theme-1", "theme-2", "theme-3", "theme-4", "theme-5", "theme-6"), 5),
        (("theme-1",), 0),
        (("theme-1",), 11),
    ],
)
@pytest.mark.asyncio
async def test_catalog_rejects_invalid_candidate_queries(
    theme_ids: tuple[str, ...],
    limit_per_theme: int,
) -> None:
    uow = _Uow()
    catalog = AnalysisContextualPassageCatalog(uow)

    with pytest.raises(ValueError):
        await catalog.find_active_by_themes(
            theme_ids,
            limit_per_theme=limit_per_theme,
        )

    assert uow.entries == 0

