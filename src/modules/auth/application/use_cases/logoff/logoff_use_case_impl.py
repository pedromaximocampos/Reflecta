from typing import Optional
from src.modules.auth.application.services.auth_session import IAuthSessionService
from src.modules.auth.application.use_cases.logoff.ilogoff_use_case import ILogoffUseCase
from src.modules.auth.domain.entities.auth_session import AuthSession
from src.domain.exceptions.api_types import AuthError
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork


class LogoffUseCaseImpl(ILogoffUseCase):

    def __init__(self, auth_session_service: IAuthSessionService, auth_unit_of_work: IAuthUnitOfWork) -> None:
        self.__auth_session_service = auth_session_service
        self.__auth_unit_of_work = auth_unit_of_work

    async def execute(self, refresh_token: str) -> None:
        async with self.__auth_unit_of_work as uow:

            session: Optional[AuthSession] = await self.__auth_session_service.validate_session_by_refresh_token(
                refresh_token, uow)

            if not session:
                raise AuthError("Sessão inválida ou expirou.")

            await self.__auth_session_service.invalidate_session(session, uow)
            await uow.commit()
