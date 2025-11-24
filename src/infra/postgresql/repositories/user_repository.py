from sqlalchemy.exc import IntegrityError

from src.domain.exceptions.custom_exceptions.user_custom_exceptions import EmailAlreadyExistsError, \
    UsernameAlreadyExistsError
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.infra.postgresql.connection import DBConnectionHandler
from src.infra.postgresql.mappers.user_mapper import UserMapper
from src.infra.postgresql.models import UserModel, AuthCredentialsModel
from src.domain.entities.user import User, AuthCredentials
from sqlalchemy import select, Result, Row, update
from typing import Optional

class UserRepository(IUserRepository):

    def __init__(self, db: DBConnectionHandler, user_mapper: UserMapper):
        self._db = db
        self._user_mapper = user_mapper

    async def find_by_id(self, user_id: str) -> Optional[User]:
        pass

    async def find_by_email(self, email: str) -> Optional[User]:
        async with self._db.session() as session:
            query =  (
                select(UserModel, AuthCredentialsModel)
                .join(AuthCredentialsModel, UserModel.id == AuthCredentialsModel.user_id)
                .where(UserModel.email == email)
            )
            row: Row[tuple[UserModel, AuthCredentialsModel]] = (await session.execute(query)).first()

            if not row:
                return None

            user_model, credentials_model = row

            user_entity: User = self._user_mapper.to_entity(user_model=user_model, auth_credentials_model=credentials_model)

            return user_entity

    async def update(self, user: User) -> None:
       pass

    async def update_auth_credentials(self, user: User) -> None:
        creds: AuthCredentials = user.auth_credentials

        async with self._db.session() as session:
            auth_query = (
                update(AuthCredentialsModel)
                .where(AuthCredentialsModel.user_id == creds.user_id)
                .values(
                    password_hash=creds.password.hash,
                    password_algorithm=creds.password.algorithm,
                    password_version=creds.password.version,
                    last_password_change=creds.last_password_change
                )
            )
            await session.execute(auth_query)

    async def update_last_login_at(self, user:User) -> None:

        async with self._db.session() as session:
            user_query = (
                update(UserModel)
                .where(UserModel.id == user.id)
                .values(last_login_at=user.last_login_at)
            )

            await session.execute(user_query)


    async def create(self, user: User) -> User:
        try:
            async with self._db.session() as session:
                user_model, creds_model = self._user_mapper.to_model(user)

                session.add(user_model)
                session.add(creds_model)

            return self._user_mapper.to_entity(
                user_model=user_model,
                auth_credentials_model=creds_model,
            )

        except IntegrityError as e:
            constraint = str(e.orig).lower()

            if "users_email_key" in constraint:
                raise EmailAlreadyExistsError()
            if "users_username_key" in constraint:
                raise UsernameAlreadyExistsError()

            raise