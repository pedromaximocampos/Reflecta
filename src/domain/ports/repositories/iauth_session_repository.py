from abc import ABC, abstractmethod
from src.domain.entities.auth_session import AuthSession
from src.domain.value_objects.token_jti import TokenJti
from src.domain.value_objects.user_id import UserId
from typing import Optional


class IAuthSessionRepository(ABC):

    @abstractmethod
    async def get_sessions_by_user_id(self, user_id: UserId) -> list[AuthSession]:
        """Retorna todas as sessões ativas do usuário. Ordenadas de maneira crescente pela data de criação."""
        raise NotImplementedError

    @abstractmethod
    async def revoke_session(self, session_entity: AuthSession) -> None:
        """Revoga a sessão especificada."""
        raise NotImplementedError

    @abstractmethod
    async def create_session(self, session_entity: AuthSession) -> AuthSession:
        """Cria uma nova sessão."""
        raise NotImplementedError

    @abstractmethod
    async def get_session_by_hashed_jti(self, hashed_jti: TokenJti) -> Optional[AuthSession]:
        """Retorna a sessão associada ao JTI hash fornecido."""
        raise NotImplementedError


    @abstractmethod
    async def invalidate_session(self, auth_session: AuthSession) -> None:
        """Deleta a sessão especificada pelo ID."""
        raise NotImplementedError