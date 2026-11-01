import hashlib
import secrets
from datetime import datetime, timedelta, timezone
import ulid
from sqlalchemy import select, func
from src.modules.auth.infrastructure.persistence.postgresql.models.users_model import UserModel
from src.modules.journal.infrastructure.persistence.postgresql.models.context_analysis_model import ContextAnalysisModel as Analysis
from src.modules.journal.infrastructure.persistence.postgresql.models.context_share_model import ContextShareModel as Share
from src.modules.journal.infrastructure.persistence.postgresql.models.journal_entry_model import JournalEntryModel as Entry
from src.modules.ai_processing.application.contextual_analysis import ContextResult
from src.modules.journal.public.context_analysis import ContextPeriod


class ShareUnavailable(Exception):
    pass


class ShareIneligible(Exception):
    pass


def token_digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


class ContextShareGateway:
    def __init__(self, db, clock=None):
        self.db = db
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    @staticmethod
    def owned(analysis_id, user_id):
        return select(Analysis).join(UserModel, UserModel.id == Analysis.user_id).where(
            Analysis.id == analysis_id, Analysis.user_id == user_id, UserModel.deleted_at.is_(None))

    @staticmethod
    async def sources_available(session, analysis):
        if not analysis.entry_ids:
            return False
        count = await session.scalar(select(func.count()).select_from(Entry).where(
            Entry.id.in_(analysis.entry_ids), Entry.user_id == analysis.user_id,
            Entry.deleted_at.is_(None), Entry.status != "deleted"))
        return count == len(set(analysis.entry_ids))

    @staticmethod
    def metadata(share, now):
        state = "revoked" if share.revoked_at else "expired" if share.expires_at <= now else "active"
        return {"id": share.id, "created_at": share.created_at.isoformat(), "expires_at": share.expires_at.isoformat(),
                "revoked_at": share.revoked_at.isoformat() if share.revoked_at else None, "state": state}

    async def create(self, analysis_id, user_id):
        now = self.clock()
        async with self.db.session() as session:
            analysis = await session.scalar(self.owned(analysis_id, user_id))
            if analysis is None:
                raise ShareUnavailable()
            if not analysis.period_start or len(analysis.entry_ids) < 5 or not await self.sources_available(session, analysis):
                raise ShareIneligible()
            period = ContextPeriod(start_date=analysis.period_start, end_date=analysis.period_end)
            # Whitelist the exact displayed synthesis. No owner or journal references.
            snapshot = {"period": period.describe(), "created_at": analysis.created_at.isoformat(),
                        "entry_count": len(analysis.entry_ids), "result": ContextResult.model_validate(analysis.result).model_dump()}
            token = secrets.token_urlsafe(32)
            share = Share(id=str(ulid.new()), user_id=user_id, analysis_id=analysis_id,
                token_hash=token_digest(token), snapshot=snapshot, created_at=now,
                expires_at=now + timedelta(days=3), revoked_at=None)
            session.add(share)
            return {**self.metadata(share, now), "token": token}

    async def list_shares(self, analysis_id, user_id):
        now = self.clock()
        async with self.db.session() as session:
            if await session.scalar(self.owned(analysis_id, user_id)) is None:
                raise ShareUnavailable()
            rows = (await session.execute(select(Share).where(Share.analysis_id == analysis_id, Share.user_id == user_id)
                .order_by(Share.created_at.desc(), Share.id.desc()))).scalars().all()
            return {"shares": [self.metadata(row, now) for row in rows]}

    async def revoke(self, analysis_id, share_id, user_id):
        async with self.db.session() as session:
            if await session.scalar(self.owned(analysis_id, user_id)) is None:
                raise ShareUnavailable()
            share = await session.scalar(select(Share).where(Share.id == share_id, Share.analysis_id == analysis_id,
                Share.user_id == user_id).with_for_update())
            if share is None:
                raise ShareUnavailable()
            share.revoked_at = share.revoked_at or self.clock()
            return self.metadata(share, self.clock())

    async def resolve(self, token):
        now = self.clock()
        async with self.db.session() as session:
            share = await session.scalar(select(Share).join(UserModel, UserModel.id == Share.user_id).where(
                Share.token_hash == token_digest(token), Share.revoked_at.is_(None), Share.expires_at > now,
                UserModel.deleted_at.is_(None)))
            if share is None:
                raise ShareUnavailable()
            analysis = await session.scalar(self.owned(share.analysis_id, share.user_id))
            if analysis is None or not await self.sources_available(session, analysis):
                raise ShareUnavailable()
            # Revalidate the whitelist even for stored snapshots; never forward extras.
            snapshot = share.snapshot
            period = ContextPeriod.model_validate({k: snapshot["period"][k] for k in ("start_date", "end_date")})
            return {"period": period.describe(), "created_at": snapshot["created_at"],
                    "entry_count": snapshot["entry_count"], "result": ContextResult.model_validate(snapshot["result"]).model_dump(),
                    "expires_at": share.expires_at.isoformat()}
