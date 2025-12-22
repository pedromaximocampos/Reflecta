from __future__ import annotations

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from base_unit_of_work import SQLAlchemyUnitOfWork
from src.domain.ports.repositories.iauth_session_repository import IAuthSessionRepository
from src.domain.ports.repositories.ireset_password_repository import IResetPasswordRepository
from src.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.ports.system.iclock import IClock

from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.infra.postgresql.connection import DBConnectionHandler
from src.infra.postgresql.mappers.auth_sessions_mapper import AuthSessionsMapper
from src.infra.postgresql.mappers.email_verification_mapper import EmailVerificationMapper
from src.infra.postgresql.mappers.reset_password_mapper import ResetPasswordMapper
from src.infra.postgresql.mappers.user_mapper import UserMapper
from src.infra.postgresql.repositories.auth_sessions_repository import AuthSessionsRepository
from src.infra.postgresql.repositories.reset_password_repository import ResetPasswordRepository
from src.infra.postgresql.repositories.user_email_verification_repository import UserEmailVerificationRepository
from src.infra.postgresql.repositories.user_repository import UserRepository


class AuthUnitOfWorkImpl(SQLAlchemyUnitOfWork, IAuthUnitOfWork):

    @property
    def users_repository(self) -> IUserRepository:
        assert self.__user_repository is not None
        return self.__user_repository

    @property
    def reset_password_repository(self) -> IResetPasswordRepository:
        assert self.__reset_password_repository is not None
        return self.__reset_password_repository

    @property
    def auth_sessions_repository(self) -> IAuthSessionRepository:
        assert self.__auth_sessions_repository is not None
        return self.__auth_sessions_repository

    @property
    def user_email_verification_repository(self) -> IUserEmailVerificationRepository:
        assert self.__user_email_verification_repository is not None
        return self.__user_email_verification_repository


    def __init__(self, db: DBConnectionHandler, system_clock: IClock, user_mapper: UserMapper,
                 email_verification_mapper: EmailVerificationMapper,  auth_session_mapper: AuthSessionsMapper, reset_password_mapper:
                 ResetPasswordMapper) -> None:

        super().__init__(db)
        self.__user_mapper = user_mapper
        self.__email_verification_mapper = email_verification_mapper
        self.__auth_session_mapper = auth_session_mapper
        self.__reset_password_mapper = reset_password_mapper
        self._system_clock = system_clock

        self.__user_repository: Optional[IUserRepository] = None
        self.__user_email_verification_repository: Optional[IUserEmailVerificationRepository] = None
        self.__auth_sessions_repository: Optional[IAuthSessionRepository] = None
        self.__reset_password_repository: Optional[IResetPasswordRepository] = None


    async def _init_repositories(self, session: AsyncSession) -> None:
        """
        Inicializa os repositórios com a sessão fornecida.
        :param session: session criada pelo Unit of Work ao entrar no contexto
        :return: None
        """
        self.__user_repository = UserRepository(session, self.__user_mapper)

        self.__user_email_verification_repository = UserEmailVerificationRepository(session, self.__email_verification_mapper)

        self.__auth_sessions_repository = AuthSessionsRepository(session, self.__auth_session_mapper, self._system_clock)

        self.__reset_password_repository = ResetPasswordRepository(session, self.__reset_password_mapper)

