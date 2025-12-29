from src.application.use_cases.auth.request_password_reset.request_password_reset_use_case_impl import IRequestPasswordResetUseCase
from src.presentation.http_types import HttpRequest, HttpResponse
from src.presentation.interfaces.controller_interface import IControllerInterface


class RequestResetPasswordController(IControllerInterface):

    def __init__(self, request_reset_password_use_case: IRequestPasswordResetUseCase):
        self.__request_reset_password_use_case = request_reset_password_use_case



    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        user_email = request.body.get("email", None)

        await self.__request_reset_password_use_case.execute(user_email)

        return HttpResponse(status_code=200, body={"message": "A password reset link has been sent."})