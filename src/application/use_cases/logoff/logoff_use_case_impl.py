from typing import Optional
from src.application.services.auth_session.iauth_session_service import IAuthSessionService
from src.application.use_cases.logoff.ilogoff_use_case import ILogoffUseCase
from src.domain.entities.auth_session import AuthSession
from src.domain.exceptions.api_types import AuthError


class LogoffUseCaseImpl(ILogoffUseCase):

    def __init__(self, auth_session_service: IAuthSessionService):
        self._auth_session_service = auth_session_service

    async def execute(self, refresh_token: str) -> None:
        session: Optional[AuthSession] = await self._auth_session_service.validate_session_by_refresh_token(
            refresh_token)

        if not session:
            raise AuthError("Sessão inválida ou expirou.")

        await self._auth_session_service.invalidate_session(session.id)
