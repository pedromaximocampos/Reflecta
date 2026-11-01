from src.modules.journal.public.analysis import USER_REPROCESS_LIMIT, UserReprocessLimitError, reprocess_policy
from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_reprocess_model import AnalysisReprocessModel
import json
import ulid
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select, update

# Register the referenced users table when this gateway runs outside the API.
from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import UserModel  # noqa: F401

from src.modules.journal.domain.exceptions.journal_exceptions import JournalEntryNotFoundError
from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_sentence_model import JournalSentenceModel
from src.modules.journal.infrastructure.persistence.postgresql.models.sentence_passage_model import SentencePassageModel
from src.modules.journal.infrastructure.persistence.postgresql.models.sentence_theme_model import SentenceThemeModel
from src.modules.journal.public.analysis import AnalysisConflictError, AnalysisFailure, EntrySnapshot, SentenceAnalysis
from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler


class JournalAnalysisGateway:
    def __init__(self, db: DBConnectionHandler) -> None:
        self.db = db

    @staticmethod
    def _snapshot(entry: JournalEntryModel) -> EntrySnapshot:
        return EntrySnapshot(
            entry.id, entry.user_id, entry.content_text, entry.context_tags,
            entry.updated_at, entry.status,
            getattr(entry, "processing_settings", None),
        )

    @staticmethod
    def _query(entry_id: str, user_id: str):
        return select(JournalEntryModel).where(
            JournalEntryModel.id == entry_id,
            JournalEntryModel.user_id == user_id,
            JournalEntryModel.deleted_at.is_(None),
        )

    @staticmethod
    def _check(entry: JournalEntryModel | None) -> JournalEntryModel:
        if entry is None:
            raise JournalEntryNotFoundError()
        if entry.status not in {"draft", "pending_analysis", "analysis_failed"}:
            raise AnalysisConflictError("Entry is not eligible for interpretation.")
        return entry

    async def read(self, entry_id: str, user_id: str) -> EntrySnapshot:
        async with self.db.session() as session:
            entry = (await session.execute(self._query(entry_id, user_id))).scalar_one_or_none()
            return self._snapshot(self._check(entry))

    @staticmethod
    def _latest_failure(entry_id):
        return select(AnalysisModel.id).where(AnalysisModel.journal_entry_id == entry_id,
            AnalysisModel.status == "failed").order_by(AnalysisModel.created_at.desc(), AnalysisModel.id.desc()).limit(1)

    @staticmethod
    def _validate_text(entry):
        if not entry.content_text.strip() or len(entry.content_text.strip()) > 20000:
            raise ValueError("Entry must contain between 1 and 20000 characters.")

    async def submit(self, entry_id: str, user_id: str, *, now: datetime, expected_revision: datetime | None = None):
        async with self.db.session() as session:
            entry = (await session.execute(self._query(entry_id, user_id).with_for_update())).scalar_one_or_none()
            entry = self._check(entry)
            if entry.status == "pending_analysis":
                return {"entry_id": entry.id, "status": entry.status, "reprocess": reprocess_policy(entry)}
            self._validate_text(entry)
            if entry.status == "analysis_failed":
                used = entry.user_reprocess_count or 0
                if used >= USER_REPROCESS_LIMIT:
                    raise UserReprocessLimitError()
                if expected_revision is None or expected_revision != (entry.updated_at or entry.created_at):
                    raise AnalysisConflictError("Refresh analysis status before retrying.")
                failure_id = await session.scalar(self._latest_failure(entry.id))
                entry.user_reprocess_count = used + 1
                session.add(AnalysisReprocessModel(id=str(ulid.new()), entry_id=entry.id, failure_id=failure_id,
                    requested_by=user_id, actor_role="USER", user_attempt_number=used + 1, requested_at=now))
            entry.status = "pending_analysis"
            entry.processing_settings = None
            entry.updated_at = now
            return {"entry_id": entry.id, "status": entry.status, "reprocess": reprocess_policy(entry)}

    async def admin_reprocess(self, failure_id: str, admin_id: str, *, now: datetime, processing_settings=None):
        async with self.db.session() as session:
            query = select(JournalEntryModel).join(AnalysisModel, AnalysisModel.journal_entry_id == JournalEntryModel.id).where(
                AnalysisModel.id == failure_id, AnalysisModel.status == "failed", JournalEntryModel.deleted_at.is_(None),
            ).with_for_update(of=JournalEntryModel)
            entry = (await session.execute(query)).scalar_one_or_none()
            if entry is None:
                raise JournalEntryNotFoundError()
            latest_id = await session.scalar(self._latest_failure(entry.id))
            if latest_id != failure_id or entry.status not in {"analysis_failed", "pending_analysis"}:
                raise AnalysisConflictError("Failure no longer eligible for reprocessing.")
            if entry.status == "pending_analysis":
                return {"entry_id": entry.id, "status": entry.status, "already_pending": True,
                        "reprocess": reprocess_policy(entry)}
            self._validate_text(entry)
            if processing_settings is not None:
                from src.modules.ai_processing.application.processing_settings import AnalysisProcessingSettings
                processing_settings = AnalysisProcessingSettings.model_validate(processing_settings).model_dump()
            session.add(AnalysisReprocessModel(id=str(ulid.new()), entry_id=entry.id, failure_id=failure_id,
                requested_by=admin_id, actor_role="ADMIN", user_attempt_number=None, requested_at=now,
                processing_settings=processing_settings))
            entry.status = "pending_analysis"
            entry.processing_settings = processing_settings
            entry.updated_at = now
            return {"entry_id": entry.id, "status": entry.status, "already_pending": False,
                    "reprocess": reprocess_policy(entry)}

    async def get_analysis(self, entry_id: str, user_id: str) -> dict[str, Any]:
        async with self.db.session() as session:
            entry = (await session.execute(self._query(entry_id, user_id))).scalar_one_or_none()
            if entry is None:
                raise JournalEntryNotFoundError()
            result = (await session.execute(select(AnalysisModel).where(
                AnalysisModel.journal_entry_id == entry_id,
                AnalysisModel.status == "completed",
            ).order_by(AnalysisModel.created_at.desc(), AnalysisModel.id.desc()).limit(1))).scalar_one_or_none()
            sentences = []
            if result is not None:
                rows = (await session.execute(
                    select(JournalSentenceModel, SentenceThemeModel)
                    .outerjoin(SentenceThemeModel, SentenceThemeModel.sentence_id == JournalSentenceModel.id)
                    .where(JournalSentenceModel.analysis_id == result.id,
                           JournalSentenceModel.journal_entry_id == entry_id)
                    .order_by(JournalSentenceModel.sentence_index, SentenceThemeModel.theme_id)
                )).all()
                labels = {theme["id"]: theme for theme in (result.content_meta or {}).get("themes", [])}
                by_id = {}
                for sentence, theme in rows:
                    if sentence.id not in by_id:
                        item = {
                            "id": sentence.id, "sentence_index": sentence.sentence_index,
                            "sentence_text": sentence.sentence_text,
                            "start_offset": sentence.start_offset, "end_offset": sentence.end_offset,
                            "themes": [],
                            "passages": [],
                        }
                        by_id[sentence.id] = item
                        sentences.append(item)
                    if theme is not None:
                        by_id[sentence.id]["themes"].append({
                            **labels.get(theme.theme_id, {}), "id": theme.theme_id,
                            "slug": theme.theme_slug, "confidence": float(theme.confidence),
                            "source": theme.source, "confirmed_by_user": theme.confirmed_by_user,
                        })
                if by_id:
                    passage_rows = (await session.execute(
                        select(SentencePassageModel)
                        .where(SentencePassageModel.sentence_id.in_(by_id))
                        .order_by(
                            SentencePassageModel.sentence_id,
                            SentencePassageModel.confidence.desc(),
                            SentencePassageModel.passage_id,
                        )
                    )).scalars().all()
                    for passage in passage_rows:
                        by_id[passage.sentence_id]["passages"].append({
                            "id": passage.id,
                            "passage_id": passage.passage_id,
                            "confidence": float(passage.confidence),
                            "reason": passage.reason,
                            "payload_snapshot": passage.payload_snapshot,
                        })
            return {
                "entry_id": entry.id, "status": entry.status, "reprocess": reprocess_policy(entry),
                "analysis": None if result is None else {
                    "id": result.id, "summary": result.summary,
                    "main_message": result.main_message,
                    "metadata": result.content_meta,
                    "sentences": sentences,
                    "analyzed_at": result.analyzed_at.isoformat() if result.analyzed_at else None,
                },
            }

    async def get_analysis_failures(self, entry_id: str, user_id: str, *, limit: int = 20) -> dict[str, Any]:
        async with self.db.session() as session:
            entry = (await session.execute(self._query(entry_id, user_id))).scalar_one_or_none()
            if entry is None:
                raise JournalEntryNotFoundError()
            rows = (await session.execute(select(AnalysisModel).where(
                AnalysisModel.journal_entry_id == entry_id,
                AnalysisModel.status == "failed",
            ).order_by(AnalysisModel.created_at.desc(), AnalysisModel.id.desc()).limit(limit))).scalars().all()
            failures = []
            for row in rows:
                from src.modules.operations.application.diagnostics import safe_diagnostic
                diagnostic = safe_diagnostic(raw=row.analysis_error)
                failures.append({
                    "id": row.id, **diagnostic,
                    "failed_at": row.created_at.isoformat(),
                })
            return {
                "entry_id": entry.id, "status": entry.status,
                "can_reprocess": entry.status == "analysis_failed",
                "failures": failures,
            }

    async def next_pending(self, entry_id: str | None = None) -> EntrySnapshot | None:
        async with self.db.session() as session:
            query = select(JournalEntryModel).where(
                JournalEntryModel.status == "pending_analysis",
                JournalEntryModel.deleted_at.is_(None),
            ).order_by(JournalEntryModel.created_at, JournalEntryModel.id).limit(1)
            if entry_id is not None:
                query = query.where(JournalEntryModel.id == entry_id)
            entry = (await session.execute(query)).scalar_one_or_none()
            return self._snapshot(entry) if entry is not None else None

    async def mark_failed(self, snapshot: EntrySnapshot, *, now: datetime, failure: AnalysisFailure) -> None:
        async with self.db.session() as session:
            # The guarded transition and failure record commit together. A stale
            # worker must not append a failure to a newer or completed attempt.
            result = await session.execute(update(JournalEntryModel).where(
                JournalEntryModel.id == snapshot.entry_id,
                JournalEntryModel.user_id == snapshot.user_id,
                JournalEntryModel.deleted_at.is_(None),
                JournalEntryModel.status == "pending_analysis",
                JournalEntryModel.updated_at == snapshot.updated_at,
            ).values(status="analysis_failed", updated_at=now, processing_settings=None).returning(JournalEntryModel.id))
            if result.scalar_one_or_none() is None:
                return
            session.add(AnalysisModel(
                id=str(ulid.new()), journal_entry_id=snapshot.entry_id,
                status="failed", summary=None, main_message=None, content_meta=None,
                analysis_error=json.dumps(asdict(failure), ensure_ascii=False),
                analyzed_at=None, created_at=now, updated_at=now,
            ))

    async def save(
        self, snapshot: EntrySnapshot, *, analysis_id: str, summary: str,
        main_message: str, metadata: dict[str, Any], now: datetime,
        sentences: tuple[SentenceAnalysis, ...],
    ) -> None:
        async with self.db.session() as session:
            # Serialize competing results on the owning entry, after the API call.
            entry = (await session.execute(
                self._query(snapshot.entry_id, snapshot.user_id).with_for_update()
            )).scalar_one_or_none()
            entry = self._check(entry)
            if self._snapshot(entry) != snapshot:
                raise AnalysisConflictError("Entry changed during interpretation.")
            completed = await session.scalar(select(AnalysisModel.id).where(
                AnalysisModel.journal_entry_id == snapshot.entry_id,
                AnalysisModel.status == "completed",
            ).limit(1))
            if completed is not None:
                raise AnalysisConflictError("Entry already has a completed analysis.")
            session.add(AnalysisModel(
                id=analysis_id, journal_entry_id=snapshot.entry_id,
                summary=summary, main_message=main_message, content_meta=metadata,
                status="completed", analyzed_at=now, analysis_error=None,
                created_at=now, updated_at=now,
            ))
            # Flush parents explicitly: these models have no ORM relationships
            # to establish insert ordering across the foreign keys.
            await session.flush()
            for sentence in sentences:
                session.add(JournalSentenceModel(
                    id=sentence.id, journal_entry_id=snapshot.entry_id, analysis_id=analysis_id,
                    sentence_index=sentence.sentence_index, sentence_text=sentence.sentence_text,
                    start_offset=sentence.start_offset, end_offset=sentence.end_offset, created_at=now,
                ))
            await session.flush()
            for sentence in sentences:
                for theme in sentence.themes:
                    session.add(SentenceThemeModel(
                        sentence_id=sentence.id, theme_id=theme["id"], theme_slug=theme["slug"],
                        confidence=theme["confidence"], source="ai", confirmed_by_user=False,
                        created_at=now,
                    ))
                for passage in sentence.passages:
                    session.add(SentencePassageModel(
                        id=passage.id,
                        sentence_id=sentence.id,
                        passage_id=passage.passage_id,
                        confidence=Decimal(str(passage.confidence)),
                        reason=passage.reason,
                        payload_snapshot=passage.payload_snapshot,
                        created_at=now,
                    ))
            entry.status = "analyzed"
            entry.processing_settings = None
            entry.updated_at = now
            # Analysis, sentences, associations and entry status commit together.
