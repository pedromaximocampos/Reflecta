from src.modules.journal.public.analysis import reprocess_policy
from sqlalchemy import and_, column, table, select, literal, String, Integer, union_all, func, or_
from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_model import AnalysisModel as Analysis
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel as Entry
from src.modules.journal.infrastructure.persistence.postgresql.models.analysis_reprocess_model import AnalysisReprocessModel as Reprocess
from src.modules.internal_events.infrastructure.persistence.postgresql.models.outbox_model import OutboxModel as Outbox
from src.modules.operations.application.diagnostics import safe_diagnostic, safe_outbox_diagnostic


def processing_table(name, schema, *names):
    # Read models for tables created by the existing ingestion/inbox migrations.
    return table(name, *(column(name) for name in names), schema=schema)


Ingestion = processing_table("work_ingestions", "catalog_schema", "id", "work_id", "status", "attempts", "created_at", "finished_at", "error_code")
Chunk = processing_table("work_ingestion_chunks", "ai_processing_schema", "id", "ingestion_id", "status", "attempts", "created_at", "updated_at", "error_code")
Inbox = processing_table("inbox_events", "ai_processing_schema", "consumer_name", "event_id", "status", "attempts", "received_at", "updated_at", "error_code")


def failure_rows():
    missing = lambda: literal(None, type_=String)
    journal = select(literal("journal").label("source"), Analysis.id.label("id"),
        Entry.id.label("entity_id"), missing().label("related_id"), Entry.status.label("state"),
        Analysis.created_at.label("occurred_at"), Entry.updated_at.label("updated_at"),
        literal(None, type_=Integer).label("attempts"), Analysis.analysis_error.label("raw"), missing().label("code"),
    ).join(Entry, Entry.id == Analysis.journal_entry_id).where(Analysis.status == "failed")
    ingestion = select(literal("work_ingestion"), Ingestion.c.id, Ingestion.c.id, Ingestion.c.work_id,
        Ingestion.c.status, func.coalesce(Ingestion.c.finished_at, Ingestion.c.created_at),
        Ingestion.c.finished_at, Ingestion.c.attempts, missing(), Ingestion.c.error_code,
    ).where(or_(Ingestion.c.status == "failed", Ingestion.c.error_code.is_not(None)))
    chunk = select(literal("work_chunk"), Chunk.c.id, Chunk.c.id, Chunk.c.ingestion_id,
        Chunk.c.status, Chunk.c.updated_at, Chunk.c.updated_at, Chunk.c.attempts, missing(), Chunk.c.error_code,
    ).where(or_(Chunk.c.status == "failed", Chunk.c.error_code.is_not(None)))
    inbox = select(literal("inbox"), Inbox.c.consumer_name + literal(":") + Inbox.c.event_id,
        Inbox.c.event_id, Outbox.payload["ingestion_id"].as_string(),
        Inbox.c.status, Inbox.c.updated_at, Inbox.c.updated_at,
        Inbox.c.attempts, missing(), Inbox.c.error_code,
    ).select_from(
        Inbox.outerjoin(Outbox, Outbox.id == Inbox.c.event_id)
    ).where(or_(Inbox.c.status == "failed", Inbox.c.error_code.is_not(None)))
    outbox = select(literal("outbox"), Outbox.id, Outbox.id,
        Outbox.payload["ingestion_id"].as_string(),
        Outbox.status.cast(String), func.coalesce(Outbox.failed_at, Outbox.created_at),
        Outbox.failed_at, Outbox.attempts, Outbox.last_error, literal("event_delivery_failed"),
    ).where(or_(Outbox.failed_at.is_not(None), Outbox.status == "FAILED"))
    return union_all(journal, ingestion, chunk, inbox, outbox).subquery("operational_failures")


class OperationalFailureGateway:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def serialize(row):
        diagnostic = (
            safe_outbox_diagnostic(raw=row["raw"], attempts=row["attempts"])
            if row["source"] == "outbox"
            else safe_diagnostic(
                raw=row["raw"],
                code=row["code"],
                attempts=row["attempts"],
            )
        )
        return {"source": row["source"], "id": row["id"], "entity_id": row["entity_id"],
                "related_id": row["related_id"], "state": row["state"],
                "occurred_at": row["occurred_at"].isoformat(),
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                **diagnostic}

    async def latest_active_for_ingestions(self, ingestion_ids):
        """Return the latest unresolved operational failure per ingestion."""
        values = tuple(
            ingestion_id.value if hasattr(ingestion_id, "value") else str(ingestion_id)
            for ingestion_id in ingestion_ids
        )
        if not values:
            return {}

        rows = failure_rows()
        query = (
            select(rows)
            .where(
                or_(
                    and_(
                        rows.c.source == "work_ingestion",
                        rows.c.entity_id.in_(values),
                        rows.c.state == "failed",
                    ),
                    and_(
                        rows.c.source == "work_chunk",
                        rows.c.related_id.in_(values),
                        rows.c.state == "failed",
                    ),
                    and_(
                        rows.c.source == "outbox",
                        rows.c.related_id.in_(values),
                        rows.c.state == "FAILED",
                    ),
                    and_(
                        rows.c.source == "inbox",
                        rows.c.related_id.in_(values),
                        rows.c.state == "failed",
                    ),
                )
            )
            .order_by(rows.c.occurred_at.desc(), rows.c.id.desc())
        )
        async with self.db.session() as session:
            records = (await session.execute(query)).mappings().all()

        latest = {}
        for row in records:
            ingestion_id = (
                row["entity_id"]
                if row["source"] == "work_ingestion"
                else row["related_id"]
            )
            if ingestion_id not in latest:
                latest[ingestion_id] = self.serialize(row)
        return latest

    async def list_failures(self, *, source=None, state=None, entity_id=None, since=None, until=None, limit=20, offset=0):
        rows = failure_rows()
        query = select(rows)
        for value, field in [(source, rows.c.source), (state, rows.c.state), (entity_id, rows.c.entity_id)]:
            if value is not None:
                query = query.where(field == value)
        if since is not None:
            query = query.where(rows.c.occurred_at >= since)
        if until is not None:
            query = query.where(rows.c.occurred_at <= until)
        async with self.db.session() as session:
            total = await session.scalar(select(func.count()).select_from(query.subquery()))
            records = (await session.execute(query.order_by(rows.c.occurred_at.desc(), rows.c.source, rows.c.id.desc())
                                             .limit(limit).offset(offset))).mappings().all()
            return {"failures": [self.serialize(row) for row in records], "total": total, "limit": limit, "offset": offset}

    async def detail(self, source, failure_id):
        rows = failure_rows()
        async with self.db.session() as session:
            row = (await session.execute(select(rows).where(rows.c.source == source, rows.c.id == failure_id))).mappings().one_or_none()
            if row is None:
                return None
            result = self.serialize(row)
            if source == "journal":
                entry = await session.scalar(select(Entry).where(Entry.id == row["entity_id"]))
                latest = await session.scalar(select(Analysis.id).where(Analysis.journal_entry_id == row["entity_id"],
                    Analysis.status == "failed").order_by(Analysis.created_at.desc(), Analysis.id.desc()).limit(1))
                result["reprocess"] = reprocess_policy(entry)
                result["can_admin_reprocess"] = entry.deleted_at is None and entry.status == "analysis_failed" and latest == failure_id
                audit = await session.scalar(select(Reprocess).where(Reprocess.entry_id == entry.id,
                    Reprocess.requested_at <= row["occurred_at"])
                    .order_by(Reprocess.requested_at.desc(), Reprocess.id.desc()).limit(1))
                result["processing_settings"] = audit.processing_settings if audit is not None else None
            return result
