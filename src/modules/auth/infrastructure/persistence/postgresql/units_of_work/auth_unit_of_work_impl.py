from __future__ import annotations

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.entities.auth_session import AuthSession
from src.modules.auth.domain.entities.email_verification import EmailVerification
from src.modules.internal_events.public import OutboxEvent
from src.modules.auth.domain.entities.reset_password import ResetPassword
from src.modules.auth.domain.entities.user import User
from src.modules.internal_events.public import IOutboxRepository
from src.shared.infrastructure.persistence.postgresql.units_of_work.base_unit_of_work import SQLAlchemyUnitOfWork
from src.modules.auth.domain.ports.repositories.iauth_session_repository import IAuthSessionRepository
from src.modules.auth.domain.ports.repositories.ireset_password_repository import IResetPasswordRepository
from src.modules.auth.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.modules.auth.domain.ports.repositories.iuser_repository import IUserRepository
from src.shared.domain.ports.system.iclock import IClock

from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler

from src.modules.auth.infrastructure.persistence.postgresql.repositories.auth_sessions_repository import AuthSessionsRepository
from src.modules.auth.infrastructure.persistence.postgresql.repositories.reset_password_repository import ResetPasswordRepository
from src.modules.auth.infrastructure.persistence.postgresql.repositories.user_email_verification_repository import UserEmailVerificationRepository
from src.modules.auth.infrastructure.persistence.postgresql.repositories.user_repository import UserRepository

from src.shared.infrastructure.persistence.postgresql.mappers.interface.imapper import IMapper
from ..models import UserModel, UserEmailVerificationModel, AuthSessionsModel
from src.modules.internal_events.infrastructure.persistence.postgresql.models.outbox_model import OutboxModel
from ..models.reset_password_model import ResetPasswordModel
from src.modules.internal_events.infrastructure.persistence.postgresql.repositories.outbox_repository import OutboxRepository


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

    @property
    def outbox_repository(self) -> IOutboxRepository:
        assert self.__outbox_repository is not None
        return self.__outbox_repository



    def __init__(self, db: DBConnectionHandler, system_clock: IClock, user_mapper: IMapper[UserModel, User],
                 email_verification_mapper: IMapper[UserEmailVerificationModel, EmailVerification],  auth_session_mapper: IMapper[AuthSessionsModel, AuthSession],
                 reset_password_mapper: IMapper[ResetPasswordModel, ResetPassword], outbox_mapper: IMapper[OutboxModel, OutboxEvent]) -> None:

        super().__init__(db)
        self.__user_mapper = user_mapper
        self.__email_verification_mapper = email_verification_mapper
        self.__auth_session_mapper = auth_session_mapper
        self.__reset_password_mapper = reset_password_mapper
        self.__outbox_mapper = outbox_mapper

        self._system_clock = system_clock

        self.__user_repository: Optional[IUserRepository] = None
        self.__user_email_verification_repository: Optional[IUserEmailVerificationRepository] = None
        self.__auth_sessions_repository: Optional[IAuthSessionRepository] = None
        self.__reset_password_repository: Optional[IResetPasswordRepository] = None
        self.__outbox_repository: Optional[IOutboxRepository] = None


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

        self.__outbox_repository = OutboxRepository(session, self.__outbox_mapper, self._system_clock)


    def _clear_repositories(self) -> None:
        """
        Limpa as referências dos repositórios ao sair do contexto.
        :return: None
        """
        self.__user_repository = None
        self.__user_email_verification_repository = None
        self.__auth_sessions_repository = None
        self.__reset_password_repository = None
