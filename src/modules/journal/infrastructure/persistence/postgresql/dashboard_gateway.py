from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import aliased

from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import (
    AnalysisModel,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import (
    JournalEntryModel,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_sentence_model import (
    JournalSentenceModel,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.sentence_passage_model import (
    SentencePassageModel,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.sentence_theme_model import (
    SentenceThemeModel,
)
from src.modules.journal.public.dashboard import ThemeAffinity


BRAZIL_TIMEZONE = ZoneInfo("America/Sao_Paulo")


class JournalDashboardGateway:
    def __init__(self, db, clock=None) -> None:
        self.db = db
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    @staticmethod
    def _active_entries(user_id: str):
        return select(JournalEntryModel).where(
            JournalEntryModel.user_id == user_id,
            JournalEntryModel.deleted_at.is_(None),
            JournalEntryModel.status != "deleted",
        )

    def _month_bounds(self) -> tuple[datetime, date, date]:
        local_now = self.clock().astimezone(BRAZIL_TIMEZONE)
        start = date(local_now.year, local_now.month, 1)
        if local_now.month == 12:
            stop = date(local_now.year + 1, 1, 1)
        else:
            stop = date(local_now.year, local_now.month + 1, 1)
        return local_now, start, stop

    @staticmethod
    def _theme_rows_query(user_id: str):
        latest = aliased(AnalysisModel)
        latest_analysis_id = (
            select(latest.id)
            .where(
                latest.journal_entry_id == JournalEntryModel.id,
                latest.status == "completed",
            )
            .order_by(latest.created_at.desc(), latest.id.desc())
            .limit(1)
            .correlate(JournalEntryModel)
            .scalar_subquery()
        )
        return (
            select(AnalysisModel.content_meta, JournalEntryModel.id)
            .join(
                JournalEntryModel,
                JournalEntryModel.id == AnalysisModel.journal_entry_id,
            )
            .where(
                JournalEntryModel.user_id == user_id,
                JournalEntryModel.deleted_at.is_(None),
                JournalEntryModel.status != "deleted",
                AnalysisModel.status == "completed",
                AnalysisModel.id == latest_analysis_id,
            )
        )

    @staticmethod
    def _aggregate_themes(rows: list[Any]) -> list[ThemeAffinity]:
        themes: dict[str, dict[str, Any]] = {}
        entry_ids: dict[str, set[str]] = defaultdict(set)
        for metadata, entry_id in rows:
            metadata = metadata if isinstance(metadata, dict) else {}
            selected = metadata.get("user_theme_selection")
            selected_ids = (
                {theme_id for theme_id in selected.get("theme_ids", []) if isinstance(theme_id, str)}
                if isinstance(selected, dict) and isinstance(selected.get("theme_ids"), list)
                else None
            )
            raw_themes = metadata.get("themes")
            for theme in raw_themes if isinstance(raw_themes, list) else []:
                if not isinstance(theme, dict):
                    continue
                theme_id = theme.get("id")
                label = theme.get("label")
                if not isinstance(theme_id, str) or not theme_id or not label or (selected_ids is not None and theme_id not in selected_ids):
                    continue
                themes.setdefault(
                    theme_id,
                    {
                        "theme_id": theme_id,
                        "slug": theme.get("slug") or theme_id,
                        "label": label,
                        "color": theme.get("color"),
                    },
                )
                entry_ids[theme_id].add(entry_id)
        return sorted(
            (
                ThemeAffinity(
                    **theme,
                    reflection_count=len(entry_ids[theme_id]),
                )
                for theme_id, theme in themes.items()
            ),
            key=lambda item: (
                -item["reflection_count"],
                item["label"].casefold(),
                item["theme_id"],
            ),
        )

    async def theme_affinities(
        self,
        user_id: str,
        *,
        limit: int = 5,
    ) -> tuple[ThemeAffinity, ...]:
        if not 1 <= limit <= 20:
            raise ValueError("Theme affinity limit must be between 1 and 20.")
        async with self.db.session() as session:
            rows = (await session.execute(self._theme_rows_query(user_id))).all()
        return tuple(self._aggregate_themes(rows)[:limit])

    async def summary(self, user_id: str) -> dict[str, Any]:
        local_now, month_start, month_stop = self._month_bounds()
        async with self.db.session() as session:
            reflections_this_month = await session.scalar(
                select(func.count()).select_from(
                    self._active_entries(user_id)
                    .where(
                        JournalEntryModel.entry_date >= month_start,
                        JournalEntryModel.entry_date < month_stop,
                    )
                    .subquery()
                )
            )
            total_reflections = await session.scalar(
                select(func.count()).select_from(
                    self._active_entries(user_id).subquery()
                )
            )
            theme_rows = (
                await session.execute(self._theme_rows_query(user_id))
            ).all()
            latest = aliased(AnalysisModel)
            latest_analysis_id = (
                select(latest.id)
                .where(
                    latest.journal_entry_id == JournalEntryModel.id,
                    latest.status == "completed",
                )
                .order_by(latest.created_at.desc(), latest.id.desc())
                .limit(1)
                .correlate(JournalEntryModel)
                .scalar_subquery()
            )
            passage_rows = (await session.execute(
                select(
                    SentencePassageModel,
                    AnalysisModel.content_meta,
                    SentenceThemeModel.theme_id,
                )
                .join(
                    JournalSentenceModel,
                    JournalSentenceModel.id == SentencePassageModel.sentence_id,
                )
                .join(
                    JournalEntryModel,
                    JournalEntryModel.id == JournalSentenceModel.journal_entry_id,
                )
                .join(
                    AnalysisModel,
                    AnalysisModel.id == JournalSentenceModel.analysis_id,
                )
                .join(
                    SentenceThemeModel,
                    SentenceThemeModel.sentence_id == JournalSentenceModel.id,
                )
                .where(
                    JournalEntryModel.user_id == user_id,
                    JournalEntryModel.deleted_at.is_(None),
                    JournalEntryModel.status != "deleted",
                    AnalysisModel.id == latest_analysis_id,
                    SentencePassageModel.payload_snapshot.is_not(None),
                )
                .order_by(
                    SentencePassageModel.created_at.desc(),
                    SentencePassageModel.id.desc(),
                )
                .limit(200)
            )).all()

        themes = self._aggregate_themes(theme_rows)
        latest_reference = None
        latest_passage = None
        for passage, metadata, sentence_theme_id in passage_rows:
            metadata = metadata if isinstance(metadata, dict) else {}
            selection = metadata.get("user_theme_selection")
            raw_themes = metadata.get("themes")
            selected_ids = (
                {theme_id for theme_id in selection.get("theme_ids", []) if isinstance(theme_id, str)}
                if isinstance(selection, dict) and isinstance(selection.get("theme_ids"), list)
                else ({theme.get("id") for theme in raw_themes
                       if isinstance(theme, dict) and isinstance(theme.get("id"), str)}
                      if isinstance(raw_themes, list) else set())
            )
            snapshot = passage.payload_snapshot if isinstance(passage.payload_snapshot, dict) else {}
            matches = snapshot.get("theme_matches")
            matched_ids = {
                match.get("theme_id") for match in matches
                if isinstance(match, dict) and match.get("theme_id")
            } if isinstance(matches, list) else set()
            if sentence_theme_id in selected_ids and (not matched_ids or sentence_theme_id in matched_ids):
                latest_passage = passage
                break
        if latest_passage is not None:
            snapshot = latest_passage.payload_snapshot if isinstance(latest_passage.payload_snapshot, dict) else {}
            work = snapshot.get("work") if isinstance(snapshot.get("work"), dict) else {}
            if snapshot.get("short_text") and work.get("title"):
                latest_reference = {
                    "passage_id": latest_passage.passage_id,
                    "short_text": snapshot["short_text"],
                    "work_id": work.get("id"),
                    "work_title": work["title"],
                    "author_name": work.get("author_name"),
                    "locator": snapshot.get("locator"),
                }

        return {
            "period": {"month": local_now.month, "year": local_now.year},
            "metrics": {
                "reflections_this_month": int(reflections_this_month or 0),
                "total_reflections": int(total_reflections or 0),
                "explored_themes": len(themes),
            },
            "recurring_themes": themes[:5],
            "latest_reference": latest_reference,
        }

