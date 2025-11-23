from src.application.services.auth_session.iauth_session_service import IAuthSessionService
from src.application.use_cases.logoff.ilogoff_use_case import ILogoffUseCase
from src.application.services.auth_session.dto import AuthSessionResultDTO
from src.domain.exceptions.api_types import AuthError


class LogoffUseCaseImpl(ILogoffUseCase):

    def __init__(self, auth_session_service: IAuthSessionService):
        self._auth_session_service = auth_session_service


    async def execute(self, refresh_token: str) -> None:

        session: AuthSessionResultDTO = await self._auth_session_service.validate_session_by_refresh_token(refresh_token)

        if not session:
            raise AuthError("Sessão inválida ou expirou.")

        await self._auth_session_service.invalidate_session(session.session_id)

