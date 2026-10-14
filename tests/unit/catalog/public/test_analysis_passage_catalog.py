from datetime import UTC, datetime

import pytest

from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.public.analysis_passage_catalog import AnalysisPassageCatalog
from src.modules.catalog.public.passage_candidate import (
    PassageSuggestion,
    PassageThemeSuggestion,
)
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


class _Clock:
    def now(self):
        return datetime(2026, 10, 8, tzinfo=UTC)


class _Ids:
    def __init__(self):
        self.counter = 0

    def generate_ulid(self):
        self.counter += 1
        return f"01KPASSAGE{self.counter:016d}"


class _Repository:
    def __init__(self):
        self.calls = []

    async def replace_ai_candidates_for_chunk(self, **kwargs):
        self.calls.append(kwargs)


class _Uow:
    def __init__(self, repository):
        self.passage_repository = repository
        self.commits = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.commits += 1


@pytest.mark.asyncio
async def test_gateway_creates_pending_review_candidate_with_stable_source_key() -> (
    None
):
    repository = _Repository()
    uow = _Uow(repository)
    gateway = AnalysisPassageCatalog(uow, _Ids(), _Clock())
    suggestion = PassageSuggestion(
        exact_text="A qualidade dos pensamentos transforma a experiência da vida.",
        paraphrase="Pensamentos influenciam a experiência.",
        interpretation_note="Relaciona atenção, julgamento e bem-estar.",
        start_page=4,
        end_page=5,
        start_offset=120,
        end_offset=183,
        themes=(PassageThemeSuggestion("theme-1", 0.94),),
    )
    ingestion_id = WorkIngestionId("ingestion-1")
    work_id = WorkId("work-1")

    await gateway.replace_chunk_suggestions(
        ingestion_id=ingestion_id,
        work_id=work_id,
        chunk_id="chunk-1",
        suggestions=(suggestion,),
    )
    await gateway.replace_chunk_suggestions(
        ingestion_id=ingestion_id,
        work_id=work_id,
        chunk_id="chunk-1",
        suggestions=(suggestion,),
    )

    first = repository.calls[0]["passages"][0]
    second = repository.calls[1]["passages"][0]
    assert first.status is CatalogStatus.PENDING_REVIEW
    assert first.locator == "pp. 4-5"
    assert first.source_key == second.source_key
    assert first.id != second.id
    assert uow.commits == 2


@pytest.mark.asyncio
async def test_overlapping_chunks_share_the_same_passage_source_key() -> None:
    repository = _Repository()
    gateway = AnalysisPassageCatalog(_Uow(repository), _Ids(), _Clock())
    suggestion = PassageSuggestion(
        exact_text="A mesma passagem apareceu na sobreposição entre dois chunks.",
        paraphrase="Uma passagem repetida pelo overlap.",
        interpretation_note="A identidade deve considerar sua posição na obra.",
        start_page=10,
        end_page=10,
        start_offset=900,
        end_offset=960,
        themes=(PassageThemeSuggestion("theme-1", 0.9),),
    )
    ingestion_id = WorkIngestionId("ingestion-1")
    work_id = WorkId("work-1")

    await gateway.replace_chunk_suggestions(
        ingestion_id=ingestion_id,
        work_id=work_id,
        chunk_id="chunk-1",
        suggestions=(suggestion,),
    )
    await gateway.replace_chunk_suggestions(
        ingestion_id=ingestion_id,
        work_id=work_id,
        chunk_id="chunk-2",
        suggestions=(suggestion,),
    )

    first = repository.calls[0]["passages"][0]
    second = repository.calls[1]["passages"][0]
    assert first.source_key == second.source_key
    assert first.source_chunk_id != second.source_chunk_id
