from abc import ABC, abstractmethod
from src.domain.entities.user import User
from src.application.services.auth_session.dto import AuthSessionResultDTO
from datetime import datetime
from typing import Optional

class IAuthSessionService(ABC):

    """Contrato do serviço de sessão."""

    @abstractmethod
    async def create_session(self, user: User) -> AuthSessionResultDTO:
        """Cria uma nova sessão para o usuário e retorna o ID da sessão."""
        raise NotImplementedError

    @abstractmethod
    async def validate_session_by_refresh_token(self, refresh_token: str) -> Optional[AuthSessionResultDTO]:
        """Valida a sessão e retorna o ID do usuário associado."""
        raise NotImplementedError

    @abstractmethod
    async def invalidate_session(self, session_id: str) -> None:
        """Invalida a sessão com base no ID da sessão."""
        raise NotImplementedError