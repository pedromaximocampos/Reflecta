from abc import ABC, abstractmethod
from src.domain.entities.auth_session import AuthSession

class IAuthSessionRepository(ABC):

    @abstractmethod
    async def get_sessions_by_user_id(self, user_id: str) -> list[AuthSession]:
        """Retorna todas as sessões ativas do usuário."""
        raise NotImplementedError

    @abstractmethod
    async def revoke_session(self, session: AuthSession) -> None:
        """Revoga a sessão especificada."""
        raise NotImplementedError

    @abstractmethod
    async def create_session(self, session: AuthSession) -> AuthSession:
        """Cria uma nova sessão."""
        raise NotImplementedError