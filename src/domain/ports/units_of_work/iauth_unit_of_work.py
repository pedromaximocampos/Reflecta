from contextlib import AbstractAsyncContextManager
from typing import Protocol


from src.domain.ports.repositories.iauth_session_repository import IAuthSessionRepository
from src.domain.ports.repositories.ireset_password_repository import IResetPasswordRepository
from src.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.domain.ports.repositories.iuser_repository import IUserRepository


class IAuthUnitOfWork(Protocol):

    @property
    def users_repository(self) -> IUserRepository:
        ...

    @property
    def reset_password_repository(self) -> IResetPasswordRepository:
        ...

    @property
    def auth_sessions_repository(self) -> IAuthSessionRepository:
        ...


    @property
    def user_email_verification_repository(self) -> IUserEmailVerificationRepository:
        ...


    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...