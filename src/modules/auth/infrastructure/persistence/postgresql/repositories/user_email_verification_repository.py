from __future__ import annotations

from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.postgresql.mappers.interface.imapper import IMapper
from src.modules.auth.infrastructure.persistence.postgresql.models import UserEmailVerificationModel
from src.modules.auth.domain.entities.email_verification import EmailVerification
from src.modules.auth.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.modules.auth.infrastructure.persistence.postgresql.mappers.email_verification_mapper import EmailVerificationMapper


class UserEmailVerificationRepository(IUserEmailVerificationRepository):
    def __init__(self, session: AsyncSession, mapper: IMapper[UserEmailVerificationModel, EmailVerification]) -> None:
        self._session = session
        self._mapper = mapper

    async def create_verification_code(self, email_verification: EmailVerification) -> EmailVerification:
        model = self._mapper.to_model(email_verification)
        self._session.add(model)

        # garante INSERT sem commit (commit fica no UoW)
        await self._session.flush()

        # se você precisa de valores gerados pelo DB (defaults server-side), mantenha refresh
        await self._session.refresh(model)

        return self._mapper.to_entity(model)

    async def get_by_code(self, hashed_code: str) -> Optional[EmailVerification]:
        query = (
            select(UserEmailVerificationModel)
            .where(UserEmailVerificationModel.token_hash == hashed_code)
        )
        model = (await self._session.execute(query)).scalar_one_or_none()
        return None if not model else self._mapper.to_entity(model)

    async def revoke(self, email_verification: EmailVerification) -> None:
        model = self._mapper.to_model(email_verification)
        query = (
            update(UserEmailVerificationModel)
            .where(UserEmailVerificationModel.id == model.id)
            .values(revoked_at=model.revoked_at)
        )
        await self._session.execute(query)

    async def mark_as_verified(self, email_verification: EmailVerification) -> None:
        model = self._mapper.to_model(email_verification)
        query = (
            update(UserEmailVerificationModel)
            .where(UserEmailVerificationModel.id == model.id)
            .values(verified_at=model.verified_at)
        )
        await self._session.execute(query)

    async def get_active_email_verification_by_user_id(self, user_id: UserId) -> Optional[EmailVerification]:
        query = (
            select(UserEmailVerificationModel)
            .where(
                UserEmailVerificationModel.user_id == str(user_id),
                UserEmailVerificationModel.revoked_at.is_(None),
                UserEmailVerificationModel.verified_at.is_(None),
            )
        )
        model = (await self._session.execute(query)).scalar_one_or_none()
        return None if not model else self._mapper.to_entity(model)
