from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from src.shared.domain.errors.api_types import NotFoundError
from src.modules.auth.domain.ports.repositories.ireset_password_repository import IResetPasswordRepository
from src.modules.auth.domain.entities.reset_password import ResetPassword
from src.shared.infrastructure.persistence.mappers.interface import IMapper
from src.modules.auth.infrastructure.persistence.postgresql.models.reset_password_model import ResetPasswordModel


class ResetPasswordRepository(IResetPasswordRepository):

    def __init__(self, session: AsyncSession, reset_password_mapper: IMapper[ResetPasswordModel, ResetPassword]) -> None:
        self._session = session
        self._mapper = reset_password_mapper

    async def find_by_hashed_token(self, hashed_token: str) -> Optional[ResetPassword]:
        query = (select(ResetPasswordModel)
                .where(ResetPasswordModel.token_hash == hashed_token)
        )
        result = (await self._session.execute(query)).scalar_one_or_none()
        if result:
            return self._mapper.to_entity(result)
        return None

    async def update_as_used(self, reset_password: ResetPassword, now: datetime) -> ResetPassword:
        query  = (
            update(ResetPasswordModel)
            .where(ResetPasswordModel.id == reset_password.id)
            .values(used_at=now)
            .returning(ResetPasswordModel)
        )
        result = (await self._session.execute(query)).scalar_one_or_none()

        if not result:
            raise NotFoundError("Failed to mark ResetPassword as used.")

        return self._mapper.to_entity(result)

    async def create_new_password_reset(self, reset_password: ResetPassword) -> ResetPassword:
        reset_password_model = self._mapper.to_model(reset_password)
        self._session.add(reset_password_model)
        await self._session.flush()
        return self._mapper.to_entity(reset_password_model)
