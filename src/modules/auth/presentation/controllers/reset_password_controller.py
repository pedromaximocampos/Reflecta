from src.modules.auth.application.use_cases.reset_password.ireset_password_use_case import IResetPasswordUseCase
from src.modules.auth.domain.exceptions.passwords_exceptions import ResetPasswordTokenException
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class ResetPasswordController(IControllerInterface):


    def __init__(self, reset_password_use_case: IResetPasswordUseCase) -> None:
        self.__reset_password_use_case = reset_password_use_case


    async def handle_request(self, request: HttpRequest) -> HttpResponse:

        reset_raw_token = request.body.get('reset_token', None)

        new_password = request.body.get('new_password', None)

        repeated_password = request.body.get('repeated_password', None)

        if reset_raw_token is None:
            raise ResetPasswordTokenException("Reset token is required.")

        if new_password is None:
            raise ResetPasswordTokenException("New password is required.")

        if new_password != repeated_password:
            raise ResetPasswordTokenException("Passwords do not match.")

        await self.__reset_password_use_case.execute(reset_raw_token, new_password)

        return HttpResponse(status_code=200, body={"message": "Password has been reset successfully."})

