from src.modules.auth.application.use_cases.recovery.irecovery_use_case import IRecoveryUseCase
from src.modules.auth.domain.exceptions.user_recovery_exceptions import UserRecoveryTokenError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class RecoveryController(IControllerInterface):
    def __init__(self, recovery_use_case: IRecoveryUseCase) -> None:
        self.__use_case = recovery_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        code = request.query_params.get("code")
        if not isinstance(code, str) or not code.strip():
            raise UserRecoveryTokenError("Account recovery code is required.")

        await self.__use_case.execute(code)
        return HttpResponse(
            status_code=200,
            body={"message": "Account recovered successfully. You can log in again."},
        )
