from typing import Optional
from .irefresh_use_case import IRefreshUseCase
from .dto import RefreshResultDTO
from src.application.services.auth_session import IAuthSessionService, AuthSessionResultDTO
from src.application.services.token.itoken_service import ITokenService
from src.domain.entities.auth_session import AuthSession
from src.domain.exceptions.api_types import AuthError
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.ports.system.iclock import IClock


class RefreshUseCaseImpl(IRefreshUseCase):


    def __init__(self, auth_session_service: IAuthSessionService, user_repository: IUserRepository,
                 system_clock : IClock):
        self._auth_session_service = auth_session_service
        self._user_repository = user_repository
        self._clock = system_clock


    async def execute(self, refresh_token: str) -> RefreshResultDTO:

        past_session: Optional[AuthSession] = await self._auth_session_service.validate_session_by_refresh_token(refresh_token)

        if not past_session:
            raise AuthError("Sessão inválida ou expirou.")

        user = await self._user_repository.find_by_id(past_session.user_id)

        if not user:
            raise AuthError("Usuário não encontrado para o token fornecido.")

        auth_session_result: AuthSessionResultDTO  = await self._auth_session_service.refresh_session(past_session)

        return RefreshResultDTO(
            access_token=auth_session_result.access_token,
            refresh_token=auth_session_result.refresh_token,
            user=user
        )