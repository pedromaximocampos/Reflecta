from abc import ABC, abstractmethod
from src.domain.entities.user import User
from src.application.services.auth_session.dto import AuthSessionResultDTO
from datetime import datetime

class IAuthSessionService(ABC):

    """Contrato do serviço de sessão."""

    @abstractmethod
    async def create_session(self, user: User) -> AuthSessionResultDTO:
        """Cria uma nova sessão para o usuário e retorna o ID da sessão."""
        raise NotImplementedError

    @abstractmethod
    async def validate_session(self, session_id: str) -> AuthSessionResultDTO:
        """Valida a sessão e retorna o ID do usuário associado."""
        raise NotImplementedError