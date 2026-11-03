from datetime import datetime, timezone
import ulid
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import UserModel  # noqa: F401
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel as Entry
from src.modules.journal.infrastructure.persistence.postgresql.models.context_analysis_model import ContextAnalysisModel as Context
from src.modules.journal.public.context_analysis import MIN_ENTRIES, HistoryChangedError, fingerprint


class ContextGateway:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def active(user_id):
        return select(Entry).where(Entry.user_id == user_id, Entry.deleted_at.is_(None), Entry.status != "deleted")

    @staticmethod
    def serialize(row):
        return {"id": row.id, "entry_ids": row.entry_ids, "result": row.result,
                "created_at": row.created_at.isoformat(),
                "period": {"start_date": row.period_start.isoformat(), "end_date": row.period_end.isoformat(),
                           "timezone": "America/Sao_Paulo"} if row.period_start else None}

    async def period_entries(self, user_id, period, session=None):
        if session is None:
            async with self.db.session() as session:
                return await self.period_entries(user_id, period, session)
        start, stop = period.bounds()
        rows = (await session.execute(self.active(user_id).where(Entry.created_at >= start, Entry.created_at < stop)
                                       .order_by(Entry.created_at, Entry.id))).scalars().all()
        return [{"id": row.id, "content_text": row.content_text, "context_tags": row.context_tags,
                 "created_at": row.created_at.isoformat(),
                 "updated_at": row.updated_at.isoformat() if row.updated_at else None} for row in rows]

    async def find(self, user_id, key):
        async with self.db.session() as session:
            row = await session.scalar(select(Context).where(Context.user_id == user_id, Context.fingerprint == key))
            return self.serialize(row) if row else None

    async def status(self, user_id, period):
        async with self.db.session() as session:
            entries = await self.period_entries(user_id, period, session)
            key = fingerprint(entries, period)
            row = await session.scalar(select(Context).where(Context.user_id == user_id, Context.fingerprint == key))
            return {"period": period.describe(), "entry_count": len(entries), "minimum_entries": MIN_ENTRIES, "eligible": len(entries) >= MIN_ENTRIES,
                    "analysis": self.serialize(row) if row else None}

    async def history(self, user_id, *, limit=5, offset=0):
        async with self.db.session() as session:
            owned = select(Context).where(Context.user_id == user_id)
            total = await session.scalar(select(func.count()).select_from(owned.subquery()))
            rows = (await session.execute(owned.order_by(Context.created_at.desc(), Context.id.desc())
                                          .limit(limit).offset(offset))).scalars().all()
            source_ids = {entry_id for row in rows for entry_id in row.entry_ids}
            active_ids = set()
            if source_ids:
                active_ids = set((await session.execute(select(Entry.id).where(
                    Entry.user_id == user_id, Entry.deleted_at.is_(None),
                    Entry.status != "deleted", Entry.id.in_(source_ids),
                ))).scalars().all())
            items = []
            for row in rows:
                available = bool(row.entry_ids) and all(entry_id in active_ids for entry_id in row.entry_ids)
                items.append({
                    "id": row.id, "created_at": row.created_at.isoformat(),
                    "period": self.serialize(row)["period"],
                    "entry_count": len(row.entry_ids), "available": available,
                    "entry_ids": row.entry_ids if available else [],
                    "result": row.result if available else None,
                })
            return {"analyses": items, "total": total, "limit": limit, "offset": offset}

    async def save(self, user_id, key, entries, result, period):
        async with self.db.session() as session:
            # Lock source rows before rechecking; deletion/edit waits for this commit.
            ids = [entry["id"] for entry in entries]
            await session.execute(self.active(user_id).where(Entry.id.in_(ids)).with_for_update())
            if fingerprint(await self.period_entries(user_id, period, session), period) != key:
                raise HistoryChangedError()
            await session.execute(insert(Context).values(id=str(ulid.new()), user_id=user_id,
                fingerprint=key, entry_ids=ids, result=result, period_start=period.start_date, period_end=period.end_date, created_at=datetime.now(timezone.utc))
                .on_conflict_do_nothing(constraint="uq_context_user_snapshot"))
            row = await session.scalar(select(Context).where(Context.user_id == user_id, Context.fingerprint == key))
            return self.serialize(row)
