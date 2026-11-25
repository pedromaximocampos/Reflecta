import logging

from src.modules.catalog.application.exceptions import WorkCoverStorageError
from src.modules.catalog.application.ports.storage import IWorkCoverStorage
from src.modules.catalog.domain.entities.passage import Passage
from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.domain.ports.repositories.iwork_repository import (
    WorkCatalogRecord,
)
from src.modules.catalog.domain.ports.unit_of_work import ICatalogGraphUnitOfWork
from src.modules.catalog.public.featured_work import (
    FeaturedPassage,
    FeaturedTheme,
    FeaturedWork,
)
from src.modules.catalog.public.work_id import WorkId


_LOGGER = logging.getLogger(__name__)
_MAX_PASSAGES_PER_WORK = 500
_MAX_FEATURED_THEMES = 3
_FEATURED_PASSAGE_POOL = 12


class AnalysisFeaturedWorkCatalog:
    """Builds a safe daily public projection from active catalog content."""

    def __init__(
        self,
        uow: ICatalogGraphUnitOfWork,
        cover_storage: IWorkCoverStorage,
    ) -> None:
        self._uow = uow
        self._cover_storage = cover_storage

    async def get_for_day(self, day_ordinal: int) -> FeaturedWork | None:
        if day_ordinal < 1:
            raise ValueError("Featured work day ordinal must be positive.")

        async with self._uow as uow:
            records = tuple(await uow.work_repository.list_works())
            active_records = tuple(sorted(
                (record for record in records if record.active_passage_count > 0),
                key=lambda record: record.work.id.value,
            ))
            if not active_records:
                return None

            selected = active_records[(day_ordinal - 1) % len(active_records)]
            passage_page = await uow.passage_repository.list_passages(
                status=CatalogStatus.ACTIVE,
                work_id=WorkId(selected.work.id.value),
                limit=_MAX_PASSAGES_PER_WORK,
                offset=0,
            )
            if not passage_page.passages:
                return None
            themes = tuple(await uow.theme_repository.list_themes())

        ranked_passages = sorted(
            passage_page.passages,
            key=self._passage_rank,
            reverse=True,
        )[:_FEATURED_PASSAGE_POOL]
        passage_cycle = (day_ordinal - 1) // len(active_records)
        passage = ranked_passages[passage_cycle % len(ranked_passages)]
        theme_by_id = {
            theme.id.value: theme for theme in themes if theme.is_active
        }
        theme_stats: dict[str, tuple[int, float]] = {}
        for candidate in passage_page.passages:
            for relevance in candidate.themes:
                theme_id = relevance.theme_id.value
                if theme_id not in theme_by_id:
                    continue
                count, confidence = theme_stats.get(theme_id, (0, 0.0))
                theme_stats[theme_id] = (
                    count + 1,
                    max(confidence, relevance.confidence),
                )

        ranked_theme_ids = sorted(
            theme_stats,
            key=lambda theme_id: (
                -theme_stats[theme_id][0],
                -theme_stats[theme_id][1],
                theme_by_id[theme_id].label.casefold(),
            ),
        )[:_MAX_FEATURED_THEMES]
        cover_url = await self._resolve_cover_url(selected)
        return FeaturedWork(
            work_id=selected.work.id.value,
            title=selected.work.title,
            author_name=selected.author.name,
            synopsis=selected.work.synopsis,
            cover_image_url=cover_url,
            themes=tuple(
                FeaturedTheme(
                    theme_id=theme_id,
                    label=theme_by_id[theme_id].label,
                    color=str(theme_by_id[theme_id].color),
                )
                for theme_id in ranked_theme_ids
            ),
            passage=FeaturedPassage(
                short_text=passage.short_text,
                paraphrase=passage.paraphrase,
                locator=passage.locator,
            ),
        )

    async def _resolve_cover_url(
        self,
        record: WorkCatalogRecord,
    ) -> str | None:
        if not record.work.cover_object_key:
            return record.work.cover_image_url
        try:
            return await self._cover_storage.create_read_url(
                object_key=record.work.cover_object_key
            )
        except WorkCoverStorageError:
            _LOGGER.warning(
                "Featured work cover unavailable: work_id=%s",
                record.work.id.value,
            )
            return None

    @staticmethod
    def _passage_rank(passage: Passage) -> tuple[float, float, int, int, str]:
        return (
            passage.reflective_value if passage.reflective_value is not None else -1.0,
            max((theme.confidence for theme in passage.themes), default=0.0),
            passage.priority,
            -abs(len(passage.short_text) - 240),
            passage.id.value,
        )
