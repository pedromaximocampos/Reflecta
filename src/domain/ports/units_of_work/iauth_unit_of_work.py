from __future__ import annotations

from typing import Protocol, TypeVar, Optional, Type
from types import TracebackType

from src.domain.ports.repositories.iauth_session_repository import IAuthSessionRepository
from src.domain.ports.repositories.ioutbox_repository import IOutboxRepository
from src.domain.ports.repositories.ireset_password_repository import IResetPasswordRepository
from src.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.domain.ports.repositories.iuser_repository import IUserRepository

TAuthUow = TypeVar("TAuthUow", bound="IAuthUnitOfWork")

"""
TypeVar serve pra preservar o tipo concreto quando você usa Protocol/context manager, evitando que o type checker “perca” o tipo no async with.
Assim, se uow é AuthUnitOfWorkImpl, então x continua sendo AuthUnitOfWorkImpl (ou a interface concreta correta), e o type checker fica feliz.

A ideia é:

Quando eu faço async with uow as x, o x tem o mesmo tipo concreto de uow.

Exemplo:

se uow é AuthUnitOfWorkImpl

então x também será inferido como AuthUnitOfWorkImpl (e não “apenas” IAuthUnitOfWork)

Isso evita o type checker “achatar” o tipo.

Então sim, na prática isso te permite acessar coisas extras do tipo concreto, mas o objetivo real é preservar o tipo exato.
"""

class IAuthUnitOfWork(Protocol):
    # repos
    @property
    def users_repository(self) -> IUserRepository: ...
    @property
    def reset_password_repository(self) -> IResetPasswordRepository: ...
    @property
    def auth_sessions_repository(self) -> IAuthSessionRepository: ...
    @property
    def user_email_verification_repository(self) -> IUserEmailVerificationRepository: ...
    @property
    def outbox_repository(self) -> IOutboxRepository: ...

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...

    # async context manager
    async def __aenter__(self: TAuthUow) -> TAuthUow: ...
    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None: ...