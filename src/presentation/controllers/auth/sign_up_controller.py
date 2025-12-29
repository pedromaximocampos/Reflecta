from src.application.use_cases.auth.signup import ISignUpUseCase
from src.presentation.http_types import HttpRequest, HttpResponse
from src.presentation.interfaces.controller_interface import IControllerInterface


class SignUpController(IControllerInterface):

    def __init__(self, sign_up_use_case: ISignUpUseCase) -> None:
        self._sign_up_use_case = sign_up_use_case



    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        sign_up_input = request.body

        await self._sign_up_use_case.execute(sign_up_input)

        return HttpResponse(status_code=201, body={"message": "User created successfully"})