from src.application.use_cases.auth.logoff.ilogoff_use_case import ILogoffUseCase
from src.domain.exceptions.api_types import AuthError
from src.presentation.http_types import HttpRequest, HttpResponse, Cookie
from src.presentation.interfaces.controller_interface import IControllerInterface


class LogoffController(IControllerInterface):

    def __init__(self, logoff_use_case: ILogoffUseCase):
        self._logoff_use_case = logoff_use_case


    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        """Processa a requisição de logoff do usuário."""
        refresh_token = request.pop_refresh_cookie()

        if refresh_token:
            try:
                await self._logoff_use_case.execute(refresh_token)
            except AuthError:
                # Ignora erro para manter logout idempotente
                pass


        response = HttpResponse(
            status_code=200,
            body={"message": "Logoff realizado com sucesso"},
        )

        response.set_new_cookie(
            Cookie(
                name="refresh_token",
                value="",
                max_age=0,
                http_only=True,
                secure=True,
                samesite="Lax",
                path="/",
                domain=None,
            )
        )

        return response