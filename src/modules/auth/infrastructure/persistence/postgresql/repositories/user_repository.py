from __future__ import annotations

from typing import Optional
from sqlalchemy import select, update, Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.user import User, AuthCredentials
from src.modules.auth.domain.exceptions.user_custom_exceptions import (
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
)
from src.modules.auth.domain.ports.repositories.iuser_repository import IUserRepository
from src.modules.auth.public.email import Email
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.postgresql.mappers.interface.imapper import IMapper
from src.modules.auth.infrastructure.persistence.postgresql.mappers.user_mapper import UserMapper
from src.modules.auth.infrastructure.persistence.postgresql.models import UserModel, AuthCredentialsModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession, user_mapper: IMapper[UserModel, User]) -> None:
        self.__session = session
        self.__user_mapper = user_mapper

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        query = (
            select(UserModel, AuthCredentialsModel)
            .join(AuthCredentialsModel, UserModel.id == AuthCredentialsModel.user_id)
            .where(UserModel.id == user_id.value)
        )

        row: Optional[Row[tuple[UserModel, AuthCredentialsModel]]] = (await self.__session.execute(query)).first()
        if not row:
            return None

        user_model, credentials_model = row
        return self.__user_mapper.to_entity(
            user_model,
        )

    async def find_by_email(self, email: Email) -> Optional[User]:
        query = (
            select(UserModel, AuthCredentialsModel)
            .join(AuthCredentialsModel, UserModel.id == AuthCredentialsModel.user_id)
            .where(UserModel.email == email.value)
        )

        row: Optional[Row[tuple[UserModel, AuthCredentialsModel]]] = (await self.__session.execute(query)).first()
        if not row:
            return None

        user_model, credentials_model = row
        return self.__user_mapper.to_entity(
            user_model,
        )

    async def update(self, user: User) -> None:
        query = (
            update(UserModel)
            .where(UserModel.id == user.id.value)
            .values(
                username=user.username,
                email=user.email.value,
                name=user.name,
                surname=user.surname,
                date_of_birth=user.date_of_birth,
                avatar_url=user.avatar_url,
                last_login_at=user.last_login_at,
            )
        )
        await self.__session.execute(query)

    async def update_auth_credentials(self, user: User) -> None:
        creds: AuthCredentials = user.auth_credentials

        auth_query = (
            update(AuthCredentialsModel)
            .where(AuthCredentialsModel.user_id == creds.user_id.value)
            .values(
                password_hash=creds.password.hash,
                password_algorithm=creds.password.algorithm,
                password_version=creds.password.version,
                last_password_change=creds.last_password_change,
            )
        )
        await self.__session.execute(auth_query)

    async def update_last_login_at(self, user: User) -> None:
        user_query = (
            update(UserModel)
            .where(UserModel.id == user.id.value)
            .values(last_login_at=user.last_login_at)
        )
        await self.__session.execute(user_query)

    async def create(self, user: User) -> User:
        user_model = self.__user_mapper.to_model(user)

        try:
            self.__session.add(user_model)
            self.__session.add(user_model.credentials)


            await self.__session.flush()

            # se algum default server-side existir e você precisar, pode dar refresh:
            # await self.__session.refresh(user_model)
            # await self.__session.refresh(creds_model)

            return self.__user_mapper.to_entity(user_model)

        except IntegrityError as e:
            constraint = str(getattr(e, "orig", e)).lower()

            if "ix_users_email" in constraint:
                raise EmailAlreadyExistsError()
            if "ix_users_username" in constraint:
                raise UsernameAlreadyExistsError()

            raise

    async def verify_email(self, user: User) -> User:

        user_model = self.__user_mapper.to_model(user)
        query = (
            update(UserModel)
            .where(UserModel.id == user.id.value)
            .values(
                is_email_verified=True,
                email_verified_at=user_model.email_verified_at,
            )
            .returning(UserModel)
        )

        result = await self.__session.execute(query)
        updated_user = result.scalar_one()  # ou scalar_one_or_none()

        return updated_user
