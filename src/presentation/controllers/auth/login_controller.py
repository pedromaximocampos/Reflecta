from src.application.use_cases.login import LoginInput, LoginOutput
from src.presentation.http_types import HttpRequest, HttpResponse
from src.presentation.interfaces.controller_interface import IControllerInterface
from src.application.use_cases.login.ilogin_use_case import ILoginUseCase
from basicauth import decode, encode
from src.domain.exceptions.api_types import BadRequestError

class LoginController(IControllerInterface):

    def __init__(self, login_use_case: ILoginUseCase):
        self._login_use_case = login_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        authorization_header = request.headers.get("Authorization")

        username, password = self._decode_basic_auth(authorization_header)

        login_input = LoginInput(username, password)

        login_output: LoginOutput = await self._login_use_case.execute(login_input)

        return HttpResponse(
            status_code=200,
            body={
                "access_token": login_output.access_token,
                "user": {
                    "username": login_output.username,
                    "email": login_output.email,
                    "name": login_output.name,
                    "surname": login_output.surname,
                    "avatar_url": login_output.avatar_url,
                }
            },
            headers={"refresh-token": login_output.refresh_token}
        )

    @classmethod
    def _decode_basic_auth(cls, authorization_header: str) -> tuple[str, str]:
        username, password = decode(authorization_header)

        if username is None or password is None:
            raise BadRequestError("Credenciais inválidas")

        return username, password
