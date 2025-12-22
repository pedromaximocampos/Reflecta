from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from src.domain.ports.repositories.ireset_password_repository import IResetPasswordRepository
from src.domain.entities.reset_password import ResetPassword
from src.infra.postgresql.models.reset_password_model import ResetPasswordModel


class ResetPasswordRepository(IResetPasswordRepository):

    def __init__(self, session: AsyncSession, reset_password_mapper) -> None:
        self._session = session
        self._mapper = reset_password_mapper

    async def find_by_hashed_token(self, hashed_token: str) -> Optional[ResetPassword]:
        query = await self._session.execute(
            self._mapper.select().where(ResetPasswordModel.token_hash == hashed_token)
        )
        result = query.first()
        if result:
            return self._mapper.from_record(result)
        return None

    async def update_as_used(self, reset_password: ResetPassword) -> ResetPassword:
        await self._session.execute(
            self._mapper.update()
            .where(ResetPasswordModel.id == reset_password.id)
            .values(is_used=True)
        )
        return reset_password