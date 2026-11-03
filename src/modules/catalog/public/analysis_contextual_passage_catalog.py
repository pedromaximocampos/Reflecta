from src.modules.catalog.domain.ports.unit_of_work import ICatalogGraphUnitOfWork
from src.modules.catalog.public.contextual_passage import (
    ContextualPassageCandidate,
)


MAX_CONTEXTUAL_THEMES = 5
MAX_CANDIDATES_PER_THEME = 10


class AnalysisContextualPassageCatalog:
    """Read-only public facade for active, theme-related catalog passages."""

    def __init__(self, uow: ICatalogGraphUnitOfWork) -> None:
        self._uow = uow

    async def find_active_by_themes(
        self,
        theme_ids: tuple[str, ...],
        *,
        limit_per_theme: int = 5,
    ) -> tuple[ContextualPassageCandidate, ...]:
        self._validate_request(theme_ids, limit_per_theme)
        if not theme_ids:
            return ()

        async with self._uow as uow:
            records = (
                await uow.passage_repository.find_active_contextual_candidates(
                    theme_ids=theme_ids,
                    limit_per_theme=limit_per_theme,
                )
            )
        return tuple(
            ContextualPassageCandidate(
                passage_id=record.passage_id,
                matched_theme_id=record.matched_theme_id,
                matched_theme_confidence=record.matched_theme_confidence,
                short_text=record.short_text,
                paraphrase=record.paraphrase,
                interpretation_note=record.interpretation_note,
                locator=record.locator,
                priority=record.priority,
                work_id=record.work_id,
                work_title=record.work_title,
                author_name=record.author_name,
                start_page=record.start_page,
                end_page=record.end_page,
            )
            for record in records
        )

    @staticmethod
    def _validate_request(
        theme_ids: tuple[str, ...],
        limit_per_theme: int,
    ) -> None:
        if len(theme_ids) > MAX_CONTEXTUAL_THEMES:
            raise ValueError(
                f"At most {MAX_CONTEXTUAL_THEMES} themes may be queried."
            )
        if len(theme_ids) != len(set(theme_ids)):
            raise ValueError("Theme IDs must be unique.")
        if any(not theme_id.strip() for theme_id in theme_ids):
            raise ValueError("Theme IDs must not be empty.")
        if not 1 <= limit_per_theme <= MAX_CANDIDATES_PER_THEME:
            raise ValueError(
                "The candidate limit per theme must be between 1 and "
                f"{MAX_CANDIDATES_PER_THEME}."
            )

