import hmac
from datetime import datetime, timedelta, timezone

import ulid
from sqlalchemy import func, select

from src.modules.ai_processing.application.contextual_analysis import ContextResult
from src.modules.journal.public.context_analysis import ContextPeriod
from src.modules.journal.public.context_share import (
    IJournalSharingFacade,
    JournalShareSourceIneligible,
    JournalShareSourceUnavailable,
    validate_shared_entries,
)
from src.modules.sharing.domain import ShareIneligible, ShareUnavailable
from src.modules.sharing.infrastructure.persistence.postgresql.models.context_share_model import (
    ContextShareModel,
)
from src.modules.sharing.infrastructure.security import (
    recoverable_share_token,
    token_digest,
)


class ContextShareGateway:
    def __init__(
        self,
        db,
        journal: IJournalSharingFacade,
        token_secret: str,
        clock=None,
    ) -> None:
        self._db = db
        self._journal = journal
        self._token_secret = token_secret
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @staticmethod
    def metadata(share: ContextShareModel, now: datetime) -> dict:
        state = (
            "revoked"
            if share.revoked_at
            else "expired"
            if share.expires_at <= now
            else "active"
        )
        return {
            "id": share.id,
            "created_at": share.created_at.isoformat(),
            "expires_at": share.expires_at.isoformat(),
            "revoked_at": share.revoked_at.isoformat() if share.revoked_at else None,
            "state": state,
            "includes_journals": bool(
                (getattr(share, "snapshot", None) or {}).get("entries")
            ),
        }

    def owner_metadata(self, share: ContextShareModel, now: datetime) -> dict:
        metadata = self.metadata(share, now)
        if metadata["state"] != "active":
            return metadata
        token = recoverable_share_token(share.id, self._token_secret)
        if hmac.compare_digest(share.token_hash, token_digest(token)):
            metadata["token"] = token
        return metadata

    async def create(
        self,
        analysis_id: str,
        user_id: str,
        *,
        include_journals: bool = False,
    ) -> dict:
        try:
            source = await self._journal.prepare_share(
                analysis_id,
                user_id,
                include_journals=include_journals,
            )
        except JournalShareSourceUnavailable as error:
            raise ShareUnavailable() from error
        except JournalShareSourceIneligible as error:
            raise ShareIneligible() from error

        now = self._clock()
        snapshot = {
            "schema_version": 2,
            "period": source.period,
            "created_at": source.created_at.isoformat(),
            "entry_count": source.entry_count,
            "result": source.result,
            "entries": source.entries,
        }
        share_id = str(ulid.new())
        token = recoverable_share_token(share_id, self._token_secret)
        share = ContextShareModel(
            id=share_id,
            user_id=user_id,
            analysis_id=analysis_id,
            token_hash=token_digest(token),
            snapshot=snapshot,
            created_at=now,
            expires_at=now + timedelta(days=3),
            revoked_at=None,
        )
        async with self._db.session() as session:
            session.add(share)
        return {**self.owner_metadata(share, now), "token": token}

    async def list_shares(self, analysis_id: str, user_id: str) -> dict:
        try:
            await self._journal.describe_owned(analysis_id, user_id)
        except JournalShareSourceUnavailable as error:
            raise ShareUnavailable() from error

        now = self._clock()
        async with self._db.session() as session:
            rows = (
                await session.execute(
                    select(ContextShareModel)
                    .where(
                        ContextShareModel.analysis_id == analysis_id,
                        ContextShareModel.user_id == user_id,
                    )
                    .order_by(
                        ContextShareModel.created_at.desc(),
                        ContextShareModel.id.desc(),
                    )
                )
            ).scalars().all()
        return {"shares": [self.owner_metadata(row, now) for row in rows]}

    async def list_owner_shares(
        self,
        user_id: str,
        *,
        state: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> dict:
        now = self._clock()
        conditions = [ContextShareModel.user_id == user_id]
        if state == "active":
            conditions.extend(
                [
                    ContextShareModel.revoked_at.is_(None),
                    ContextShareModel.expires_at > now,
                ]
            )
        elif state == "expired":
            conditions.extend(
                [
                    ContextShareModel.revoked_at.is_(None),
                    ContextShareModel.expires_at <= now,
                ]
            )
        elif state == "revoked":
            conditions.append(ContextShareModel.revoked_at.is_not(None))
        elif state is not None:
            raise ValueError("Invalid share state.")

        async with self._db.session() as session:
            total = await session.scalar(
                select(func.count())
                .select_from(ContextShareModel)
                .where(*conditions)
            )
            shares = (
                await session.execute(
                    select(ContextShareModel)
                    .where(*conditions)
                    .order_by(
                        ContextShareModel.created_at.desc(),
                        ContextShareModel.id.desc(),
                    )
                    .limit(limit)
                    .offset(offset)
                )
            ).scalars().all()

        descriptions = await self._journal.describe_owned_many(
            tuple(dict.fromkeys(share.analysis_id for share in shares)),
            user_id,
        )
        items = []
        for share in shares:
            analysis = descriptions.get(share.analysis_id)
            if analysis is None:
                continue
            items.append(
                {
                    **self.owner_metadata(share, now),
                    "analysis_id": analysis.analysis_id,
                    "analysis_created_at": analysis.created_at.isoformat(),
                    "period": analysis.period,
                    "entry_count": analysis.entry_count,
                    "summary": analysis.summary,
                }
            )
        return {
            "shares": items,
            "total": int(total or 0),
            "limit": limit,
            "offset": offset,
        }

    async def rotate_token(
        self,
        analysis_id: str,
        share_id: str,
        user_id: str,
    ) -> dict:
        try:
            await self._journal.describe_owned(analysis_id, user_id)
        except JournalShareSourceUnavailable as error:
            raise ShareUnavailable() from error

        now = self._clock()
        async with self._db.session() as session:
            share = await session.scalar(
                select(ContextShareModel)
                .where(
                    ContextShareModel.id == share_id,
                    ContextShareModel.analysis_id == analysis_id,
                    ContextShareModel.user_id == user_id,
                    ContextShareModel.revoked_at.is_(None),
                    ContextShareModel.expires_at > now,
                )
                .with_for_update()
            )
            if share is None:
                raise ShareUnavailable()
            token = recoverable_share_token(share.id, self._token_secret)
            share.token_hash = token_digest(token)
            return {**self.owner_metadata(share, now), "token": token}

    async def revoke(
        self,
        analysis_id: str,
        share_id: str,
        user_id: str,
    ) -> dict:
        try:
            await self._journal.describe_owned(analysis_id, user_id)
        except JournalShareSourceUnavailable as error:
            raise ShareUnavailable() from error

        async with self._db.session() as session:
            share = await session.scalar(
                select(ContextShareModel)
                .where(
                    ContextShareModel.id == share_id,
                    ContextShareModel.analysis_id == analysis_id,
                    ContextShareModel.user_id == user_id,
                )
                .with_for_update()
            )
            if share is None:
                raise ShareUnavailable()
            share.revoked_at = share.revoked_at or self._clock()
            return self.metadata(share, self._clock())

    async def resolve(self, token: str) -> dict:
        now = self._clock()
        async with self._db.session() as session:
            share = await session.scalar(
                select(ContextShareModel).where(
                    ContextShareModel.token_hash == token_digest(token),
                    ContextShareModel.revoked_at.is_(None),
                    ContextShareModel.expires_at > now,
                )
            )
        if share is None:
            raise ShareUnavailable()

        try:
            await self._journal.ensure_available(share.analysis_id, share.user_id)
        except JournalShareSourceUnavailable as error:
            raise ShareUnavailable() from error

        snapshot = share.snapshot
        period = ContextPeriod.model_validate(
            {key: snapshot["period"][key] for key in ("start_date", "end_date")}
        )
        entries = validate_shared_entries(snapshot.get("entries", []))
        return {
            "period": period.describe(),
            "created_at": snapshot["created_at"],
            "entry_count": snapshot["entry_count"],
            "result": ContextResult.model_validate(snapshot["result"]).model_dump(),
            "entries": entries,
            "includes_journals": bool(entries),
            "expires_at": share.expires_at.isoformat(),
        }
