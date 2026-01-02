from src.application.use_cases.auth.login import LoginInput, LoginOutput
from src.domain.ports.system.iclock import IClock
from src.domain.value_objects.email import Email
from src.presentation.http_types import HttpRequest, HttpResponse, Cookie
from src.presentation.interfaces.controller_interface import IControllerInterface
from src.application.use_cases.auth.login.ilogin_use_case import ILoginUseCase
from basicauth import decode
from src.domain.exceptions.api_types import BadRequestError

class LoginController(IControllerInterface):

    def __init__(self, login_use_case: ILoginUseCase, system_clock: IClock):
        self._login_use_case = login_use_case
        self._system_clock = system_clock

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        authorization_header = request.headers.get("authorization")

        username, password = self._decode_basic_auth(authorization_header)

        try:
            email = Email(username)
        except ValueError:
            raise BadRequestError("Email inválido")

        login_input = LoginInput(email, password)

        login_output: LoginOutput = await self._login_use_case.execute(login_input)
        cookies = []
        refresh_token_cookie = Cookie(
            name="refresh_token",
            value=login_output.refresh_token,
            http_only=True,
            secure=True,
            path="/",
            max_age=self._system_clock.refresh_token_expiration_in_seconds()
        )
        cookies.append(refresh_token_cookie)

        return HttpResponse(
            status_code=200,
            body={
                "access_token": login_output.access_token,
                "user": {
                    "username": login_output.username,
                    "email": login_output.email.value,
                    "name": login_output.name,
                    "surname": login_output.surname,
                    "avatar_url": login_output.avatar_url,
                }
            },
            cookies=cookies
        )

    @classmethod
    def _decode_basic_auth(cls, authorization_header: str) -> tuple[str, str]:
        username, password = decode(authorization_header)

        if username is None or password is None:
            raise BadRequestError("Credenciais inválidas")

        return username, password
