# tests/support/doubles/auth_session_service_spy.py
from typing import Dict, List, Optional

from src.application.services.auth.auth_session import IAuthSessionService
from src.application.services.auth.auth_session.dto import AuthSessionResultDTO
from src.domain.entities.auth_session import AuthSession
from src.domain.entities.user import User


class AuthSessionServiceSpy(IAuthSessionService):
    """
    Spy de IAuthSessionService para testes de login/logoff/refresh.

    - Mantém sessões em memória (por id e por refresh_token)
    - Registra chamadas de create/validate/invalidate/refresh
    - Permite configurar o retorno padrão de AuthSessionResultDTO
    """

    def __init__(self) -> None:
        # sessões em memória
        self.sessions_by_id: Dict[str, AuthSession] = {}
        self.sessions_by_refresh_token: Dict[str, AuthSession] = {}

        # registros de chamadas
        self.create_session_calls: List[User] = []
        self.validate_by_refresh_calls: List[str] = []
        self.invalidate_session_calls: List[str] = []
        self.refresh_session_calls: List[AuthSession] = []

        # retorno padrão
        self._default_auth_result = AuthSessionResultDTO(
            access_token="access-token-test",
            refresh_token="refresh-token-test",
        )

    # helpers

    def set_default_auth_result(self, result: AuthSessionResultDTO) -> None:
        self._default_auth_result = result

    def add_session(self, session: AuthSession) -> None:
        """
        Adiciona uma sessão pré-existente em memória.
        Útil para testar logoff/refresh referenciando refresh_token ou id.
        """
        # aqui assumo que AuthSession tem 'id' e 'refresh_token'
        session_id = str(getattr(session, "id", None) or getattr(session, "session_id"))
        self.sessions_by_id[session_id] = session
        self.sessions_by_refresh_token[session.refresh_token] = session

    # implementação do contrato

    async def create_session(self, user: User) -> AuthSessionResultDTO:
        self.create_session_calls.append(user)
        # se você quiser, poderia criar uma AuthSession real e armazenar aqui
        return self._default_auth_result

    async def validate_session_by_refresh_token(
        self,
        refresh_token: str,
    ) -> Optional[AuthSession]:
        self.validate_by_refresh_calls.append(refresh_token)
        return self.sessions_by_refresh_token.get(refresh_token)

    async def invalidate_session(self, session_id: str) -> None:
        self.invalidate_session_calls.append(session_id)

        session = self.sessions_by_id.pop(session_id, None)
        if session is not None:
            self.sessions_by_refresh_token.pop(session.refresh_token, None)

    async def refresh_session(self, session: AuthSession) -> AuthSessionResultDTO:
        self.refresh_session_calls.append(session)
        # poderia atualizar algo na sessão aqui, se fizer sentido
        return self._default_auth_result
