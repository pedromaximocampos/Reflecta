from collections import defaultdict
from typing import Any

from sqlalchemy import select

from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import (
    AnalysisModel,
)
from src.modules.journal.infrastructure.persistence.postgresql.models.context_analysis_model import (
    ContextAnalysisModel,
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
from src.modules.journal.public.data_export import (
    IJournalDataExportFacade,
    JournalDataExport,
)


def _iso(value) -> str | None:
    return value.isoformat() if value is not None else None


class PostgresJournalDataExportFacade(IJournalDataExportFacade):
    """Build a portable read model without exposing embeddings or operational data."""

    def __init__(self, db) -> None:
        self._db = db

    async def export_journal(self, user_id: str) -> JournalDataExport:
        async with self._db.session() as session:
            entries = (
                await session.execute(
                    select(JournalEntryModel)
                    .where(JournalEntryModel.user_id == user_id)
                    .order_by(
                        JournalEntryModel.entry_date,
                        JournalEntryModel.created_at,
                        JournalEntryModel.id,
                    )
                )
            ).scalars().all()
            entry_ids = [entry.id for entry in entries]

            analyses = []
            sentences = []
            themes = []
            passages = []
            if entry_ids:
                analyses = (
                    await session.execute(
                        select(AnalysisModel)
                        .where(AnalysisModel.journal_entry_id.in_(entry_ids))
                        .order_by(AnalysisModel.created_at, AnalysisModel.id)
                    )
                ).scalars().all()
                analysis_ids = [analysis.id for analysis in analyses]
                if analysis_ids:
                    sentences = (
                        await session.execute(
                            select(JournalSentenceModel)
                            .where(JournalSentenceModel.analysis_id.in_(analysis_ids))
                            .order_by(
                                JournalSentenceModel.analysis_id,
                                JournalSentenceModel.sentence_index,
                                JournalSentenceModel.id,
                            )
                        )
                    ).scalars().all()
                    sentence_ids = [sentence.id for sentence in sentences]
                    if sentence_ids:
                        themes = (
                            await session.execute(
                                select(SentenceThemeModel)
                                .where(SentenceThemeModel.sentence_id.in_(sentence_ids))
                                .order_by(
                                    SentenceThemeModel.sentence_id,
                                    SentenceThemeModel.theme_slug,
                                    SentenceThemeModel.theme_id,
                                )
                            )
                        ).scalars().all()
                        passages = (
                            await session.execute(
                                select(SentencePassageModel)
                                .where(SentencePassageModel.sentence_id.in_(sentence_ids))
                                .order_by(
                                    SentencePassageModel.sentence_id,
                                    SentencePassageModel.created_at,
                                    SentencePassageModel.id,
                                )
                            )
                        ).scalars().all()

            context_analyses = (
                await session.execute(
                    select(ContextAnalysisModel)
                    .where(ContextAnalysisModel.user_id == user_id)
                    .order_by(ContextAnalysisModel.created_at, ContextAnalysisModel.id)
                )
            ).scalars().all()

        themes_by_sentence: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for theme in themes:
            themes_by_sentence[theme.sentence_id].append(
                {
                    "theme_id": theme.theme_id,
                    "theme_slug": theme.theme_slug,
                    "confidence": float(theme.confidence),
                    "source": theme.source,
                    "confirmed_by_user": theme.confirmed_by_user,
                    "created_at": _iso(theme.created_at),
                }
            )

        passages_by_sentence: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for passage in passages:
            passages_by_sentence[passage.sentence_id].append(
                {
                    "id": passage.id,
                    "passage_id": passage.passage_id,
                    "confidence": float(passage.confidence),
                    "reason": passage.reason,
                    "passage_snapshot": passage.payload_snapshot,
                    "created_at": _iso(passage.created_at),
                }
            )

        sentences_by_analysis: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for sentence in sentences:
            sentences_by_analysis[sentence.analysis_id].append(
                {
                    "id": sentence.id,
                    "sentence_index": sentence.sentence_index,
                    "sentence_text": sentence.sentence_text,
                    "start_offset": sentence.start_offset,
                    "end_offset": sentence.end_offset,
                    "themes": themes_by_sentence[sentence.id],
                    "passages": passages_by_sentence[sentence.id],
                    "created_at": _iso(sentence.created_at),
                }
            )

        analyses_by_entry: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for analysis in analyses:
            analyses_by_entry[analysis.journal_entry_id].append(
                {
                    "id": analysis.id,
                    "summary": analysis.summary,
                    "main_message": analysis.main_message,
                    "content": analysis.content_meta,
                    "status": analysis.status,
                    "analyzed_at": _iso(analysis.analyzed_at),
                    "created_at": _iso(analysis.created_at),
                    "updated_at": _iso(analysis.updated_at),
                    "sentences": sentences_by_analysis[analysis.id],
                }
            )

        exported_entries = tuple(
            {
                "id": entry.id,
                "title": entry.title,
                "content_text": entry.content_text,
                "context_tags": entry.context_tags,
                "status": entry.status,
                "entry_date": _iso(entry.entry_date),
                "created_at": _iso(entry.created_at),
                "updated_at": _iso(entry.updated_at),
                "deleted_at": _iso(entry.deleted_at),
                "analyses": analyses_by_entry[entry.id],
            }
            for entry in entries
        )
        exported_context = tuple(
            {
                "id": analysis.id,
                "entry_ids": analysis.entry_ids,
                "period_start": _iso(analysis.period_start),
                "period_end": _iso(analysis.period_end),
                "result": analysis.result,
                "created_at": _iso(analysis.created_at),
            }
            for analysis in context_analyses
        )
        return JournalDataExport(
            entries=exported_entries,
            context_analyses=exported_context,
        )
