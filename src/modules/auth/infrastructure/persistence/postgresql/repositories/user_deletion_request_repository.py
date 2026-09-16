from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.user_deletion_request import UserDeletionRequest
from src.modules.auth.domain.exceptions.user_deletion_exceptions import UserDeletionTokenError
from src.modules.auth.domain.ports.repositories.iuser_deletion_request_repository import (
    IUserDeletionRequestRepository,
)
from src.modules.auth.infrastructure.persistence.postgresql.models.user_deletion_request_model import (
    UserDeletionRequestModel,
)
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.postgresql.mappers.interface.imapper import IMapper


class UserDeletionRequestRepository(IUserDeletionRequestRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: IMapper[UserDeletionRequestModel, UserDeletionRequest],
    ) -> None:
        self.__session = session
        self.__mapper = mapper

    async def create(
        self,
        deletion_request: UserDeletionRequest,
    ) -> UserDeletionRequest:
        model = self.__mapper.to_model(deletion_request)
        self.__session.add(model)
        await self.__session.flush()
        return self.__mapper.to_entity(model)

    async def find_by_hashed_token(
        self,
        hashed_token: str,
    ) -> Optional[UserDeletionRequest]:
        query = select(UserDeletionRequestModel).where(
            UserDeletionRequestModel.token_hash == hashed_token
        )
        model = (await self.__session.execute(query)).scalar_one_or_none()
        return None if model is None else self.__mapper.to_entity(model)

    async def get_active_by_user_id(
        self,
        user_id: UserId,
    ) -> Optional[UserDeletionRequest]:
        query = select(UserDeletionRequestModel).where(
            UserDeletionRequestModel.user_id == user_id.value,
            UserDeletionRequestModel.confirmed_at.is_(None),
            UserDeletionRequestModel.revoked_at.is_(None),
        )
        model = (await self.__session.execute(query)).scalar_one_or_none()
        return None if model is None else self.__mapper.to_entity(model)

    async def revoke(self, deletion_request: UserDeletionRequest) -> None:
        query = (
            update(UserDeletionRequestModel)
            .where(
                UserDeletionRequestModel.id == deletion_request.id,
                UserDeletionRequestModel.confirmed_at.is_(None),
                UserDeletionRequestModel.revoked_at.is_(None),
            )
            .values(revoked_at=deletion_request.revoked_at)
        )
        await self.__session.execute(query)

    async def mark_as_confirmed(
        self,
        deletion_request: UserDeletionRequest,
        confirmed_at: datetime,
    ) -> None:
        query = (
            update(UserDeletionRequestModel)
            .where(
                UserDeletionRequestModel.id == deletion_request.id,
                UserDeletionRequestModel.confirmed_at.is_(None),
                UserDeletionRequestModel.revoked_at.is_(None),
            )
            .values(confirmed_at=confirmed_at)
            .returning(UserDeletionRequestModel.id)
        )
        result = await self.__session.execute(query)
        if result.scalar_one_or_none() is None:
            raise UserDeletionTokenError()
