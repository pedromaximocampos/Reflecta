from src.modules.auth.application.use_cases.refresh.dto import RefreshResultDTO
from src.modules.auth.application.use_cases.refresh.irefresh_use_case import IRefreshUseCase
from src.domain.exceptions.api_types import AuthError
from src.domain.ports.system.iclock import IClock
from src.presentation.http_types import HttpRequest, HttpResponse, Cookie
from src.presentation.interfaces.controller_interface import IControllerInterface



class RefreshController(IControllerInterface):


    def __init__(self, refresh_use_case: IRefreshUseCase, system_clock: IClock):
        self._refresh_use_case = refresh_use_case
        self._system_clock = system_clock


    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        try:
            refresh_token = request.pop_refresh_cookie()
            if not refresh_token:
                raise AuthError("Token de atualização não fornecido.")

            refresh_result: RefreshResultDTO = await self._refresh_use_case.execute(refresh_token)


            response_body = {
                "access_token": refresh_result.access_token,
                "user": {
                    "username": refresh_result.user.username,
                    "email": refresh_result.user.email.value,
                    "name": refresh_result.user.name,
                    "surname": refresh_result.user.surname,
                    "avatar_url": refresh_result.user.avatar_url,
                }
            }
            refresh_cookie = Cookie(
                    name="refresh_token",
                    value=refresh_result.refresh_token,
                    http_only=True,
                    secure=True,
                    path="/",
                    max_age=self._system_clock.refresh_token_expiration_in_seconds()
                )


            response  = HttpResponse(status_code=200, body=response_body)

            response.set_new_cookie(refresh_cookie)
            return response


        except AuthError as e:

            response = HttpResponse(status_code=401, body={"error": str(e)})

            response.set_new_cookie(Cookie(
                name="refresh_token",
                value="",
                max_age=0,
                http_only=True,
                secure=True,
                samesite="Lax",
                path="/",
                domain=None,
            ))
            return response

        except Exception as e:
            print(e)

            response = HttpResponse(status_code=500, body={"error": "Erro interno do servidor"})

            response.set_new_cookie( Cookie(
                name="refresh_token",
                value="",
                max_age=0,
                http_only=True,
                secure=True,
                samesite="Lax",
                path="/",
                domain=None,
            ))
            return response