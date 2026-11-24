from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.sharing.domain.entities import ProfessionalActivity, ShareAccess
from src.modules.sharing.domain.ports.repositories import (
    IProfessionalActivityRepository,
)
from src.modules.sharing.infrastructure.persistence.postgresql.models import (
    ContextShareModel,
    ProfessionalActivityModel,
)
from src.modules.sharing.infrastructure.security import token_digest
from src.modules.sharing.domain.value_objects import ActivityStatus
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class ProfessionalActivityRepository(IProfessionalActivityRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: IMapper[ProfessionalActivityModel, ProfessionalActivity],
    ) -> None:
        self._session = session
        self._mapper = mapper

    async def find_active_access_for_update(
        self,
        token: str,
        now: datetime,
    ) -> ShareAccess | None:
        share = await self._session.scalar(
            select(ContextShareModel)
            .where(
                ContextShareModel.token_hash == token_digest(token),
                ContextShareModel.revoked_at.is_(None),
                ContextShareModel.expires_at > now,
            )
            .with_for_update()
        )
        if share is None:
            return None
        return ShareAccess(
            id=share.id,
            user_id=share.user_id,
            analysis_id=share.analysis_id,
            expires_at=share.expires_at,
        )

    async def count_for_share(self, share_id: str) -> int:
        count = await self._session.scalar(
            select(func.count())
            .select_from(ProfessionalActivityModel)
            .where(ProfessionalActivityModel.share_id == share_id)
        )
        return int(count or 0)

    async def add_many(
        self,
        activities: tuple[ProfessionalActivity, ...],
    ) -> tuple[ProfessionalActivity, ...]:
        models = tuple(self._mapper.to_model(activity) for activity in activities)
        self._session.add_all(models)
        await self._session.flush()
        return tuple(self._mapper.to_entity(model) for model in models)

    async def list_for_user(
        self,
        user_id: str,
        status: ActivityStatus | None,
        limit: int,
        offset: int,
    ) -> tuple[ProfessionalActivity, ...]:
        query = select(ProfessionalActivityModel).where(
            ProfessionalActivityModel.user_id == user_id,
        )
        if status is not None:
            query = query.where(ProfessionalActivityModel.status == status.value)
        if status is ActivityStatus.PENDING:
            query = query.order_by(
                ProfessionalActivityModel.due_date.asc().nulls_last(),
                ProfessionalActivityModel.created_at.desc(),
            )
        else:
            query = query.order_by(ProfessionalActivityModel.created_at.desc())
        models = (
            await self._session.scalars(query.limit(limit).offset(offset))
        ).all()
        return tuple(self._mapper.to_entity(model) for model in models)

    async def count_for_user(
        self,
        user_id: str,
        status: ActivityStatus | None,
    ) -> int:
        query = (
            select(func.count())
            .select_from(ProfessionalActivityModel)
            .where(ProfessionalActivityModel.user_id == user_id)
        )
        if status is not None:
            query = query.where(ProfessionalActivityModel.status == status.value)
        return int(await self._session.scalar(query) or 0)

    async def find_for_user_for_update(
        self,
        activity_id: str,
        user_id: str,
    ) -> ProfessionalActivity | None:
        model = await self._session.scalar(
            select(ProfessionalActivityModel)
            .where(
                ProfessionalActivityModel.id == activity_id,
                ProfessionalActivityModel.user_id == user_id,
            )
            .with_for_update()
        )
        return self._mapper.to_entity(model) if model is not None else None

    async def save(
        self,
        activity: ProfessionalActivity,
    ) -> ProfessionalActivity:
        model = await self._session.scalar(
            update(ProfessionalActivityModel)
            .where(
                ProfessionalActivityModel.id == activity.id,
                ProfessionalActivityModel.user_id == activity.user_id,
            )
            .values(
                status=activity.status.value,
                completed_at=activity.completed_at,
            )
            .returning(ProfessionalActivityModel)
        )
        if model is None:
            raise RuntimeError("Professional activity disappeared during update.")
        return self._mapper.to_entity(model)

