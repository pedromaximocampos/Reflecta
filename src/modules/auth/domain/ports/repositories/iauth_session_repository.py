from src.modules.auth.domain.entities.auth_session import AuthSession
from src.modules.auth.domain.value_objects.token_jti import TokenJti
from src.modules.auth.public.user_id import UserId
from typing import Optional, Protocol


class IAuthSessionRepository(Protocol):

    async def get_sessions_by_user_id(self, user_id: UserId) -> list[AuthSession]:
        """Retorna todas as sessões ativas do usuário. Ordenadas de maneira crescente pela data de criação."""
        raise NotImplementedError

    async def revoke_session(self, session_entity: AuthSession) -> None:
        """Revoga a sessão especificada."""
        raise NotImplementedError

    async def create_session(self, session_entity: AuthSession) -> AuthSession:
        """Cria uma nova sessão."""
        raise NotImplementedError

    async def get_session_by_hashed_jti(self, hashed_jti: TokenJti) -> Optional[AuthSession]:
        """Retorna a sessão associada ao JTI hash fornecido."""
        raise NotImplementedError

    async def invalidate_session(self, auth_session: AuthSession) -> None:
        """Deleta a sessão especificada pelo ID."""
        raise NotImplementedError

    async def refresh_session(self, auth_session: AuthSession) -> AuthSession:
        """Atualiza a sessão especificada."""
        raise NotImplementedError

    async def invalidate_all_sessions_for_user(self, user_id: UserId) -> None:
        """Invalida todas as sessões associadas a um usuário específico."""
        raise NotImplementedError

