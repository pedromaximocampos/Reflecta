from sqlalchemy import select

from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_sentence_model import JournalSentenceModel
from src.modules.journal.infrastructure.persistence.postgresql.models.sentence_passage_model import SentencePassageModel
from src.modules.journal.infrastructure.persistence.postgresql.models.sentence_theme_model import SentenceThemeModel
from src.modules.journal.public.context_share import SharedJournalEntry


def _text(value, *, fallback=None):
    return value.strip() if isinstance(value, str) and value.strip() else fallback


def _public_theme(raw_theme):
    if not isinstance(raw_theme, dict):
        return None
    label = _text(raw_theme.get("label"), fallback=_text(raw_theme.get("slug")))
    if not label:
        return None
    return {"label": label, "color": _text(raw_theme.get("color"))}


class JournalShareSnapshotBuilder:
    @staticmethod
    async def _analysis(session, entry_id):
        result = await session.scalar(
            select(AnalysisModel)
            .where(
                AnalysisModel.journal_entry_id == entry_id,
                AnalysisModel.status == "completed",
            )
            .order_by(AnalysisModel.created_at.desc(), AnalysisModel.id.desc())
            .limit(1)
        )
        if result is None:
            return None

        metadata = result.content_meta if isinstance(result.content_meta, dict) else {}
        raw_themes = metadata.get("themes")
        available_themes = [
            theme for theme in raw_themes
            if isinstance(theme, dict) and isinstance(theme.get("id"), str) and theme["id"]
        ] if isinstance(raw_themes, list) else []
        available_by_id = {theme["id"]: theme for theme in available_themes}
        selection = metadata.get("user_theme_selection")
        if isinstance(selection, dict) and isinstance(selection.get("theme_ids"), list):
            selected_ids = [
                theme_id for theme_id in selection["theme_ids"]
                if isinstance(theme_id, str) and theme_id in available_by_id
            ]
        else:
            selected_ids = list(available_by_id)
        selected_id_set = set(selected_ids)
        public_themes = {
            theme_id: public_theme
            for theme_id in selected_ids
            if (public_theme := _public_theme(available_by_id[theme_id])) is not None
        }

        rows = (
            await session.execute(
                select(JournalSentenceModel, SentenceThemeModel)
                .outerjoin(
                    SentenceThemeModel,
                    SentenceThemeModel.sentence_id == JournalSentenceModel.id,
                )
                .where(
                    JournalSentenceModel.analysis_id == result.id,
                    JournalSentenceModel.journal_entry_id == entry_id,
                )
                .order_by(
                    JournalSentenceModel.sentence_index,
                    SentenceThemeModel.theme_id,
                )
            )
        ).all()
        sentence_theme_ids = {}
        for sentence, theme in rows:
            sentence_theme_ids.setdefault(sentence.id, set())
            if theme is not None and theme.theme_id in selected_id_set:
                sentence_theme_ids[sentence.id].add(theme.theme_id)

        passages = []
        if sentence_theme_ids:
            passage_rows = (
                await session.execute(
                    select(SentencePassageModel)
                    .where(SentencePassageModel.sentence_id.in_(sentence_theme_ids))
                    .order_by(
                        SentencePassageModel.sentence_id,
                        SentencePassageModel.confidence.desc(),
                        SentencePassageModel.passage_id,
                    )
                )
            ).scalars().all()
            for passage in passage_rows:
                snapshot = passage.payload_snapshot if isinstance(passage.payload_snapshot, dict) else {}
                short_text = _text(snapshot.get("short_text"))
                if not short_text:
                    continue
                matches = snapshot.get("theme_matches")
                matched_ids = {
                    match.get("theme_id") for match in matches
                    if isinstance(match, dict) and isinstance(match.get("theme_id"), str)
                } if isinstance(matches, list) else set()
                relevant_ids = sentence_theme_ids[passage.sentence_id]
                if matched_ids:
                    relevant_ids = relevant_ids & matched_ids
                visible_themes = [
                    public_themes[theme_id]
                    for theme_id in selected_ids
                    if theme_id in relevant_ids and theme_id in public_themes
                ]
                if not visible_themes:
                    continue
                work = snapshot.get("work") if isinstance(snapshot.get("work"), dict) else {}
                passages.append({
                    "short_text": short_text,
                    "work_title": _text(work.get("title")),
                    "author_name": _text(work.get("author_name")),
                    "locator": _text(snapshot.get("locator")),
                    "themes": visible_themes,
                    "reason": _text(passage.reason),
                    "paraphrase": _text(snapshot.get("paraphrase")),
                })

        return {
            "conclusion": _text(result.main_message, fallback=_text(result.summary)),
            "themes": [public_themes[theme_id] for theme_id in selected_ids if theme_id in public_themes],
            "passages": passages,
        }

    async def build(self, session, analysis, user_id):
        rows = (
            await session.execute(
                select(JournalEntryModel).where(
                    JournalEntryModel.id.in_(analysis.entry_ids),
                    JournalEntryModel.user_id == user_id,
                    JournalEntryModel.deleted_at.is_(None),
                    JournalEntryModel.status != "deleted",
                )
            )
        ).scalars().all()
        entries_by_id = {entry.id: entry for entry in rows}
        if set(entries_by_id) != set(analysis.entry_ids):
            return None

        snapshots = []
        for entry_id in analysis.entry_ids:
            entry = entries_by_id[entry_id]
            snapshots.append(
                SharedJournalEntry.model_validate({
                    "entry_date": entry.entry_date or entry.created_at.date(),
                    "title": entry.title,
                    "content_text": entry.content_text,
                    "analysis": await self._analysis(session, entry.id),
                }).model_dump(mode="json")
            )
        return snapshots
