from typing import Optional

from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from .irefresh_use_case import IRefreshUseCase
from .dto import RefreshResultDTO
from src.modules.auth.application.services.auth_session import IAuthSessionService, AuthSessionResultDTO
from src.modules.auth.domain.entities.auth_session import AuthSession
from src.shared.domain.errors.api_types import AuthError
from src.shared.domain.ports.system.iclock import IClock
from src.modules.auth.application.ports.storage import IUserAvatarStorage
from src.modules.auth.application.services.user_avatar_url_resolver import (
    resolve_user_avatar_url,
)


class RefreshUseCaseImpl(IRefreshUseCase):


    def __init__(self, auth_session_service: IAuthSessionService, auth_unit_of_work: IAuthUnitOfWork,
                 system_clock : IClock, avatar_storage: IUserAvatarStorage):
        self.__auth_session_service = auth_session_service
        self.__auth_unit_of_work = auth_unit_of_work
        self._clock = system_clock
        self.__avatar_storage = avatar_storage


    async def execute(self, refresh_token: str) -> RefreshResultDTO:

        async with self.__auth_unit_of_work as uow:

            past_session: Optional[AuthSession] = await self.__auth_session_service.validate_session_by_refresh_token(refresh_token, uow)

            if not past_session:
                raise AuthError("Invalid or expired session")

            user = await uow.users_repository.find_by_id(past_session.user_id)

            if not user:
                raise AuthError("Usuário não encontrado para o token fornecido.")

            auth_session_result: AuthSessionResultDTO  = await self.__auth_session_service.refresh_session(past_session, uow)

            await uow.commit()

            avatar_url = await resolve_user_avatar_url(user, self.__avatar_storage)

            return RefreshResultDTO(
                access_token=auth_session_result.access_token,
                refresh_token=auth_session_result.refresh_token,
                user=user,
                avatar_url=avatar_url,
            )
