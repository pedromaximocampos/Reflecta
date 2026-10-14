from datetime import UTC, datetime

import pytest

from src.modules.auth.public.user_id import UserId
from src.modules.catalog.application.use_cases.manage_passages import (
    CreatePassageInputDTO,
    CreatePassageUseCase,
    DeletePassageUseCase,
    ListPassagesInputDTO,
    ListPassagesUseCase,
    PassageThemeInputDTO,
    ReviewPassageUseCase,
    SetPassageAvailabilityUseCase,
    UpdatePassageInputDTO,
    UpdatePassageUseCase,
)
from src.modules.catalog.domain.entities import Theme, Work, WorkIngestion
from src.modules.catalog.domain.entities.passage import Passage, PassageThemeRelevance
from src.modules.catalog.domain.exceptions import (
    InactivePassageThemeError,
    InvalidPassageThemesError,
    InvalidPassageTransitionError,
)
from src.modules.catalog.domain.value_objects import (
    CatalogStatus,
    WorkDocumentLocation,
    WorkIngestionStatus,
)
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.theme_id import ThemeId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


NOW = datetime(2026, 10, 9, 12, tzinfo=UTC)


class _Clock:
    def now(self):
        return NOW


class _Ids:
    def generate_ulid(self):
        return "01K7PASSAGE00000000000000"


class _Passages:
    def __init__(self, passage=None):
        self.passage = passage
        self.pending = 0

    async def get_by_id(self, passage_id):
        return self.passage if self.passage and self.passage.id == passage_id else None

    async def create(self, passage):
        self.passage = passage
        return passage

    async def update(self, passage):
        self.passage = passage
        return passage

    async def list_passages(self, **filters):
        return [self.passage] if self.passage is not None else []

    async def count_pending_by_ingestion(self, ingestion_id):
        return self.pending


class _Themes:
    def __init__(self, theme):
        self.theme = theme

    async def get_theme_by_id(self, theme_id):
        return self.theme if self.theme.id == theme_id else None

    async def list_themes(self):
        return [self.theme]


class _Works:
    def __init__(self, work):
        self.work = work

    async def get_work_by_id(self, work_id):
        return self.work if self.work.id == work_id else None


class _GraphUow:
    def __init__(self, passage=None):
        self.passage_repository = _Passages(passage)
        self.theme_repository = _Themes(_theme())
        self.work_repository = _Works(_work())
        self.commits = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.commits += 1


class _Ingestions:
    def __init__(self, ingestion):
        self.ingestion = ingestion
        self.updates = 0

    async def find_by_id(self, ingestion_id):
        return self.ingestion if self.ingestion.id == ingestion_id else None

    async def update(self, ingestion):
        self.ingestion = ingestion
        self.updates += 1
        return ingestion


class _SqlUow:
    def __init__(self, ingestion):
        self.work_ingestion_repository = _Ingestions(ingestion)
        self.commits = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.commits += 1


def _theme() -> Theme:
    return Theme(
        id=ThemeId("01K7THEME0000000000000000"),
        slug="virtude",
        label="Virtude",
        description="Ação ética.",
        created_at=NOW,
    )


def _work() -> Work:
    return Work(
        id=WorkId("01K7WORK00000000000000000"),
        slug="obra",
        title="Obra",
        synopsis="Sinopse",
        work_type="book",
        language="pt-BR",
        status=CatalogStatus.INACTIVE,
        created_at=NOW,
    )


def _passage(status=CatalogStatus.PENDING_REVIEW) -> Passage:
    return Passage(
        id=PassageId("01K7PASSAGE00000000000000"),
        work_id=_work().id,
        ingestion_id=WorkIngestionId("01K7INGESTION000000000000"),
        source_chunk_id="01K7CHUNK00000000000000000",
        source_key="a" * 64,
        source="ai",
        locator="p. 10",
        short_text="Uma passagem suficientemente longa para ser revisada.",
        paraphrase="Uma paráfrase.",
        interpretation_note="Uma interpretação.",
        status=status,
        priority=0,
        start_page=10,
        end_page=10,
        start_offset=100,
        end_offset=155,
        themes=(PassageThemeRelevance(_theme().id, 0.9),),
        created_at=NOW,
    )


def _ingestion() -> WorkIngestion:
    return WorkIngestion(
        id=WorkIngestionId("01K7INGESTION000000000000"),
        work_id=_work().id,
        requested_by=UserId("user-1"),
        document_location=WorkDocumentLocation("bucket", "works/file.pdf"),
        created_at=NOW,
        status=WorkIngestionStatus.PENDING_REVIEW,
    )


@pytest.mark.asyncio
async def test_create_manual_passage_starts_approved() -> None:
    graph = _GraphUow()
    use_case = CreatePassageUseCase(graph, _Ids(), _Clock())

    result = await use_case.execute(
        CreatePassageInputDTO(
            work_id=_work().id,
            locator="cap. 1",
            short_text="Uma passagem manual suficientemente longa para o catálogo.",
            paraphrase="Paráfrase manual.",
            interpretation_note="Nota manual.",
            priority=2,
            themes=(PassageThemeInputDTO(_theme().id, 1.0),),
        )
    )

    assert result.source == "admin"
    assert result.status == CatalogStatus.APPROVED.value
    assert graph.commits == 1


@pytest.mark.asyncio
async def test_update_passage_replaces_content_and_themes() -> None:
    graph = _GraphUow(_passage())
    use_case = UpdatePassageUseCase(graph, _Clock())

    result = await use_case.execute(
        UpdatePassageInputDTO(
            passage_id=_passage().id,
            paraphrase="Paráfrase revisada.",
            priority=4,
            themes=(PassageThemeInputDTO(_theme().id, 0.95),),
        )
    )

    assert result.paraphrase == "Paráfrase revisada."
    assert result.priority == 4
    assert result.themes[0].label == "Virtude"
    assert result.themes[0].confidence == 0.95


@pytest.mark.asyncio
async def test_list_passages_includes_current_theme_label() -> None:
    graph = _GraphUow(_passage())
    use_case = ListPassagesUseCase(graph)

    result = await use_case.execute(ListPassagesInputDTO())

    assert len(result.passages) == 1
    assert result.passages[0].themes[0].theme_id == _theme().id
    assert result.passages[0].themes[0].label == "Virtude"


@pytest.mark.asyncio
async def test_update_passage_can_clear_optional_page_range() -> None:
    graph = _GraphUow(_passage())
    use_case = UpdatePassageUseCase(graph, _Clock())

    result = await use_case.execute(
        UpdatePassageInputDTO(
            passage_id=_passage().id,
            start_page=None,
            end_page=None,
            update_page_range=True,
        )
    )

    assert result.start_page is None
    assert result.end_page is None


@pytest.mark.asyncio
async def test_create_rejects_duplicate_theme_associations() -> None:
    graph = _GraphUow()
    use_case = CreatePassageUseCase(graph, _Ids(), _Clock())
    duplicated_theme = PassageThemeInputDTO(_theme().id, 0.9)

    with pytest.raises(InvalidPassageThemesError):
        await use_case.execute(
            CreatePassageInputDTO(
                work_id=_work().id,
                locator="cap. 1",
                short_text="Uma passagem manual suficientemente longa para o catálogo.",
                paraphrase="Paráfrase manual.",
                interpretation_note="Nota manual.",
                priority=2,
                themes=(duplicated_theme, duplicated_theme),
            )
        )


@pytest.mark.asyncio
async def test_approving_last_pending_passage_completes_ingestion() -> None:
    graph = _GraphUow(_passage())
    sql = _SqlUow(_ingestion())
    use_case = ReviewPassageUseCase(graph, sql, _Clock())

    result = await use_case.execute(_passage().id, approve=True)

    assert result.status == CatalogStatus.APPROVED.value
    assert sql.work_ingestion_repository.ingestion.status is WorkIngestionStatus.COMPLETED
    assert graph.commits == 1
    assert sql.commits == 1


@pytest.mark.asyncio
async def test_approve_rejects_a_passage_linked_to_an_inactive_theme() -> None:
    graph = _GraphUow(_passage())
    inactive_theme = _theme()
    inactive_theme.deactivate(updated_at=NOW)
    graph.theme_repository = _Themes(inactive_theme)
    use_case = ReviewPassageUseCase(graph, _SqlUow(_ingestion()), _Clock())

    with pytest.raises(InactivePassageThemeError):
        await use_case.execute(_passage().id, approve=True)

    assert graph.commits == 0


@pytest.mark.asyncio
async def test_reject_allows_a_passage_linked_to_an_inactive_theme() -> None:
    graph = _GraphUow(_passage())
    inactive_theme = _theme()
    inactive_theme.deactivate(updated_at=NOW)
    graph.theme_repository = _Themes(inactive_theme)
    sql = _SqlUow(_ingestion())
    use_case = ReviewPassageUseCase(graph, sql, _Clock())

    result = await use_case.execute(_passage().id, approve=False)

    assert result.status == CatalogStatus.REJECTED.value
    assert graph.commits == 1


@pytest.mark.asyncio
async def test_pending_passage_cannot_be_activated_before_approval() -> None:
    graph = _GraphUow(_passage())
    use_case = SetPassageAvailabilityUseCase(graph, _Clock())

    with pytest.raises(InvalidPassageTransitionError):
        await use_case.execute(_passage().id, active=True)


@pytest.mark.asyncio
async def test_delete_is_logical_and_rejects_pending_candidate() -> None:
    graph = _GraphUow(_passage())
    sql = _SqlUow(_ingestion())
    use_case = DeletePassageUseCase(graph, sql, _Clock())

    await use_case.execute(_passage().id)

    assert graph.passage_repository.passage.status is CatalogStatus.REJECTED
    assert sql.work_ingestion_repository.ingestion.status is WorkIngestionStatus.COMPLETED
