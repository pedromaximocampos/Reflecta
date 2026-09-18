from __future__ import annotations

from datetime import datetime
from typing import FrozenSet, Optional
from sqlalchemy import select, update, Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.user import User, AuthCredentials
from src.modules.auth.domain.exceptions.user_custom_exceptions import (
    EmailAlreadyExistsError,
    UserNotFoundError,
    UsernameAlreadyExistsError,
)
from src.modules.auth.domain.ports.repositories.iuser_repository import IUserRepository
from src.modules.auth.public.email import Email
from src.modules.auth.public.user_id import UserId
from src.shared.infrastructure.persistence.mappers.interface import IMapper
from src.modules.auth.infrastructure.persistence.postgresql.models import UserModel, AuthCredentialsModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession, user_mapper: IMapper[UserModel, User]) -> None:
        self.__session = session
        self.__user_mapper = user_mapper

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        query = (
            select(UserModel, AuthCredentialsModel)
            .join(AuthCredentialsModel, UserModel.id == AuthCredentialsModel.user_id)
            .where(
                UserModel.id == user_id.value,
                UserModel.deleted_at.is_(None),
            )
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
            .where(
                UserModel.email == email.value,
                UserModel.deleted_at.is_(None),
            )
        )

        row: Optional[Row[tuple[UserModel, AuthCredentialsModel]]] = (await self.__session.execute(query)).first()
        if not row:
            return None

        user_model, credentials_model = row
        return self.__user_mapper.to_entity(
            user_model,
        )

    async def find_deleted_by_email(self, email: Email) -> Optional[User]:
        query = (
            select(UserModel, AuthCredentialsModel)
            .join(AuthCredentialsModel, UserModel.id == AuthCredentialsModel.user_id)
            .where(
                UserModel.email == email.value,
                UserModel.deleted_at.is_not(None),
            )
        )
        row: Optional[Row[tuple[UserModel, AuthCredentialsModel]]] = (
            await self.__session.execute(query)
        ).first()
        if not row:
            return None
        user_model, _ = row
        return self.__user_mapper.to_entity(user_model)

    async def find_deleted_by_id(self, user_id: UserId) -> Optional[User]:
        query = (
            select(UserModel, AuthCredentialsModel)
            .join(AuthCredentialsModel, UserModel.id == AuthCredentialsModel.user_id)
            .where(
                UserModel.id == user_id.value,
                UserModel.deleted_at.is_not(None),
            )
        )
        row: Optional[Row[tuple[UserModel, AuthCredentialsModel]]] = (
            await self.__session.execute(query)
        ).first()
        if not row:
            return None
        user_model, _ = row
        return self.__user_mapper.to_entity(user_model)

    async def update(self, user: User) -> None:
        query = (
            update(UserModel)
            .where(
                UserModel.id == user.id.value,
                UserModel.deleted_at.is_(None),
            )
            .values(
                username=user.username,
                email=user.email.value,
                name=user.name,
                surname=user.surname,
                date_of_birth=user.date_of_birth,
                avatar_url=user.avatar_url,
                last_login_at=user.last_login_at,
                role=user.role,
                deleted_at=user.deleted_at,
            )
        )
        await self.__session.execute(query)

    async def update_user_info(
        self,
        user: User,
        fields_to_update: FrozenSet[str],
    ) -> None:
        allowed_values = {
            "name": user.name,
            "surname": user.surname,
            "date_of_birth": user.date_of_birth,
            "avatar_url": user.avatar_url,
        }
        if not fields_to_update or not fields_to_update.issubset(allowed_values):
            raise ValueError("Invalid fields for user information update.")

        query = (
            update(UserModel)
            .where(
                UserModel.id == user.id.value,
                UserModel.deleted_at.is_(None),
            )
            .values(**{field: allowed_values[field] for field in fields_to_update})
            .returning(UserModel.id)
        )
        result = await self.__session.execute(query)
        if result.scalar_one_or_none() is None:
            raise UserNotFoundError()

    async def update_auth_credentials(self, user: User) -> None:
        creds: AuthCredentials = user.auth_credentials

        auth_query = (
            update(AuthCredentialsModel)
            .where(
                AuthCredentialsModel.user_id == creds.user_id.value,
                AuthCredentialsModel.user.has(UserModel.deleted_at.is_(None)),
            )
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
            .where(
                UserModel.id == user.id.value,
                UserModel.deleted_at.is_(None),
            )
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
            .where(
                UserModel.id == user.id.value,
                UserModel.deleted_at.is_(None),
            )
            .values(
                is_email_verified=True,
                email_verified_at=user_model.email_verified_at,
            )
            .returning(UserModel)
        )

        result = await self.__session.execute(query)
        updated_user = result.scalar_one()  # ou scalar_one_or_none()

        return updated_user

    async def mark_as_deleted(self, user_id: UserId, deleted_at: datetime) -> None:
        query = (
            update(UserModel)
            .where(
                UserModel.id == user_id.value,
                UserModel.deleted_at.is_(None),
            )
            .values(deleted_at=deleted_at)
            .returning(UserModel.id)
        )
        result = await self.__session.execute(query)
        if result.scalar_one_or_none() is None:
            raise UserNotFoundError()

    async def mark_as_recovered(self, user_id: UserId) -> None:
        query = (
            update(UserModel)
            .where(
                UserModel.id == user_id.value,
                UserModel.deleted_at.is_not(None),
            )
            .values(deleted_at=None)
            .returning(UserModel.id)
        )
        result = await self.__session.execute(query)
        if result.scalar_one_or_none() is None:
            raise UserNotFoundError()
