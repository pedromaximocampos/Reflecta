from src.application.services.token.dto import GeneratedTokenDTO
from src.domain.entities.auth_session import AuthSession
from src.domain.entities.user import User
from src.application.services.auth_session.dto import AuthSessionResultDTO
from datetime import datetime
from typing import Optional, Protocol

from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork


class IAuthSessionService(Protocol):

    """Contrato do serviço de sessão."""

    async def create_session(self, user: User, uow: IAuthUnitOfWork) -> AuthSessionResultDTO:
        """Cria uma nova sessão para o usuário e retorna o ID da sessão."""
        raise NotImplementedError

    async def validate_session_by_refresh_token(self, refresh_token: str, uow: IAuthUnitOfWork) -> Optional[AuthSession]:
        """Valida a sessão e retorna o ID do usuário associado."""
        raise NotImplementedError

    async def invalidate_session(self, session: AuthSession, uow: IAuthUnitOfWork) -> None:
        """Invalida a sessão com base no ID da sessão."""
        raise NotImplementedError

    async def refresh_session(self, session: AuthSession, uow: IAuthUnitOfWork) -> AuthSessionResultDTO:
        """Atualiza a sessão existente e retorna novos tokens."""
        raise NotImplementedError