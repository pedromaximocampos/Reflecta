from datetime import datetime
from typing import Any

from sqlalchemy import select, update

# Register the referenced users table when this gateway runs outside the API.
from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import UserModel  # noqa: F401

from src.modules.journal.domain.exceptions.journal_exceptions import JournalEntryNotFoundError
from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel
from src.modules.journal.public.analysis import AnalysisConflictError, EntrySnapshot
from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler


class JournalAnalysisGateway:
    def __init__(self, db: DBConnectionHandler) -> None:
        self.db = db

    @staticmethod
    def _snapshot(entry: JournalEntryModel) -> EntrySnapshot:
        return EntrySnapshot(
            entry.id, entry.user_id, entry.content_text, entry.context_tags,
            entry.updated_at, entry.status,
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

    async def submit(self, entry_id: str, user_id: str, *, now: datetime) -> None:
        async with self.db.session() as session:
            entry = (await session.execute(
                self._query(entry_id, user_id).with_for_update()
            )).scalar_one_or_none()
            entry = self._check(entry)
            if not entry.content_text.strip() or len(entry.content_text.strip()) > 10000:
                raise ValueError("Entry must contain between 1 and 10000 characters.")
            if entry.status != "pending_analysis":
                entry.status = "pending_analysis"
                entry.updated_at = now

    async def get_analysis(self, entry_id: str, user_id: str) -> dict[str, Any]:
        async with self.db.session() as session:
            entry = (await session.execute(self._query(entry_id, user_id))).scalar_one_or_none()
            if entry is None:
                raise JournalEntryNotFoundError()
            result = (await session.execute(select(AnalysisModel).where(
                AnalysisModel.journal_entry_id == entry_id,
                AnalysisModel.status == "completed",
            ).order_by(AnalysisModel.created_at.desc(), AnalysisModel.id.desc()).limit(1))).scalar_one_or_none()
            return {
                "entry_id": entry.id, "status": entry.status,
                "analysis": None if result is None else {
                    "id": result.id, "summary": result.summary,
                    "main_message": result.main_message,
                    "metadata": result.content_meta,
                    "analyzed_at": result.analyzed_at.isoformat() if result.analyzed_at else None,
                },
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

    async def mark_failed(self, snapshot: EntrySnapshot, *, now: datetime) -> None:
        async with self.db.session() as session:
            await session.execute(update(JournalEntryModel).where(
                JournalEntryModel.id == snapshot.entry_id,
                JournalEntryModel.user_id == snapshot.user_id,
                JournalEntryModel.deleted_at.is_(None),
                JournalEntryModel.status == "pending_analysis",
                JournalEntryModel.updated_at == snapshot.updated_at,
            ).values(status="analysis_failed", updated_at=now))

    async def save(
        self, snapshot: EntrySnapshot, *, analysis_id: str, summary: str,
        main_message: str, metadata: dict[str, Any], now: datetime,
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
            entry.status = "analyzed"
            entry.updated_at = now
            # DBConnectionHandler commits both changes, or rolls them back together.
