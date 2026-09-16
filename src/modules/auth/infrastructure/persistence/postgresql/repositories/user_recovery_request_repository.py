from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.user_recovery_request import UserRecoveryRequest
from src.modules.auth.domain.exceptions.user_recovery_exceptions import UserRecoveryTokenError
from src.modules.auth.domain.ports.repositories.iuser_recovery_request_repository import (
    IUserRecoveryRequestRepository,
)
from src.modules.auth.infrastructure.persistence.postgresql.models.user_recovery_request_model import (
    UserRecoveryRequestModel,
)
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.postgresql.mappers.interface.imapper import IMapper


class UserRecoveryRequestRepository(IUserRecoveryRequestRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: IMapper[UserRecoveryRequestModel, UserRecoveryRequest],
    ) -> None:
        self.__session = session
        self.__mapper = mapper

    async def create(self, recovery_request: UserRecoveryRequest) -> UserRecoveryRequest:
        model = self.__mapper.to_model(recovery_request)
        self.__session.add(model)
        await self.__session.flush()
        return self.__mapper.to_entity(model)

    async def find_by_hashed_token(
        self,
        hashed_token: str,
    ) -> Optional[UserRecoveryRequest]:
        query = select(UserRecoveryRequestModel).where(
            UserRecoveryRequestModel.token_hash == hashed_token
        )
        model = (await self.__session.execute(query)).scalar_one_or_none()
        return None if model is None else self.__mapper.to_entity(model)

    async def get_active_by_user_id(
        self,
        user_id: UserId,
    ) -> Optional[UserRecoveryRequest]:
        query = select(UserRecoveryRequestModel).where(
            UserRecoveryRequestModel.user_id == user_id.value,
            UserRecoveryRequestModel.confirmed_at.is_(None),
            UserRecoveryRequestModel.revoked_at.is_(None),
        )
        model = (await self.__session.execute(query)).scalar_one_or_none()
        return None if model is None else self.__mapper.to_entity(model)

    async def revoke(self, recovery_request: UserRecoveryRequest) -> None:
        query = (
            update(UserRecoveryRequestModel)
            .where(
                UserRecoveryRequestModel.id == recovery_request.id,
                UserRecoveryRequestModel.confirmed_at.is_(None),
                UserRecoveryRequestModel.revoked_at.is_(None),
            )
            .values(revoked_at=recovery_request.revoked_at)
        )
        await self.__session.execute(query)

    async def mark_as_confirmed(
        self,
        recovery_request: UserRecoveryRequest,
        confirmed_at: datetime,
    ) -> None:
        query = (
            update(UserRecoveryRequestModel)
            .where(
                UserRecoveryRequestModel.id == recovery_request.id,
                UserRecoveryRequestModel.confirmed_at.is_(None),
                UserRecoveryRequestModel.revoked_at.is_(None),
            )
            .values(confirmed_at=confirmed_at)
            .returning(UserRecoveryRequestModel.id)
        )
        result = await self.__session.execute(query)
        if result.scalar_one_or_none() is None:
            raise UserRecoveryTokenError()
