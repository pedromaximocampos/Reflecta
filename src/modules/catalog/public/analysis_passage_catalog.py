import hashlib

from src.modules.catalog.domain.entities.passage import (
    Passage,
    PassageThemeRelevance,
)
from src.modules.catalog.domain.ports.unit_of_work import ICatalogGraphUnitOfWork
from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.public.passage_candidate import PassageSuggestion
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.theme_id import ThemeId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


class AnalysisPassageCatalog:
    """Catalog-owned gateway that stores AI suggestions as pending review."""

    def __init__(
        self,
        uow: ICatalogGraphUnitOfWork,
        ids: IULIDGenerator,
        clock: IClock,
    ) -> None:
        self._uow = uow
        self._ids = ids
        self._clock = clock

    async def replace_chunk_suggestions(
        self,
        *,
        ingestion_id: WorkIngestionId,
        work_id: WorkId,
        chunk_id: str,
        suggestions: tuple[PassageSuggestion, ...],
    ) -> None:
        now = self._clock.now()
        passages = tuple(
            Passage(
                id=PassageId(self._ids.generate_ulid()),
                work_id=work_id,
                ingestion_id=ingestion_id,
                source_chunk_id=chunk_id,
                source_key=self._source_key(
                    ingestion_id=ingestion_id,
                    suggestion=suggestion,
                ),
                locator=self._locator(suggestion.start_page, suggestion.end_page),
                short_text=suggestion.exact_text,
                paraphrase=suggestion.paraphrase,
                interpretation_note=suggestion.interpretation_note,
                status=CatalogStatus.PENDING_REVIEW,
                priority=0,
                start_page=suggestion.start_page,
                end_page=suggestion.end_page,
                start_offset=suggestion.start_offset,
                end_offset=suggestion.end_offset,
                themes=tuple(
                    PassageThemeRelevance(
                        theme_id=ThemeId(theme.theme_id),
                        confidence=theme.confidence,
                    )
                    for theme in suggestion.themes
                ),
                created_at=now,
            )
            for suggestion in suggestions
        )
        async with self._uow as uow:
            await uow.passage_repository.replace_ai_candidates_for_chunk(
                ingestion_id=ingestion_id,
                work_id=work_id,
                chunk_id=chunk_id,
                passages=passages,
            )
            await uow.commit()

    @staticmethod
    def _source_key(
        *,
        ingestion_id: WorkIngestionId,
        suggestion: PassageSuggestion,
    ) -> str:
        canonical = "|".join(
            (
                ingestion_id.value,
                str(suggestion.start_offset),
                str(suggestion.end_offset),
                suggestion.exact_text,
            )
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _locator(start_page: int, end_page: int) -> str:
        if start_page == end_page:
            return f"p. {start_page}"
        return f"pp. {start_page}-{end_page}"
