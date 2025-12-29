from src.application.use_cases.auth.reset_password import IResetPasswordUseCase
from src.domain.exceptions.custom_exceptions.passwords_exceptions import ResetPasswordTokenException
from src.presentation.http_types import HttpRequest, HttpResponse
from src.presentation.interfaces.controller_interface import IControllerInterface


class ResetPasswordController(IControllerInterface):


    def __init__(self, reset_password_use_case: IResetPasswordUseCase) -> None:
        self.__reset_password_use_case = reset_password_use_case


    async def handle_request(self, request: HttpRequest) -> HttpResponse:

        reset_raw_token = request.body.get('reset_token', None)

        new_password = request.body.get('new_password', None)

        if reset_raw_token is None:
            raise ResetPasswordTokenException("Reset token is required.")

        if new_password is None:
            raise ResetPasswordTokenException("New password is required.")

        await self.__reset_password_use_case.execute(reset_raw_token, new_password)

        return HttpResponse(status_code=200, body={"message": "Password has been reset successfully."})

