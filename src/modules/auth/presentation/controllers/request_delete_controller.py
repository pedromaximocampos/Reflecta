from src.modules.auth.application.use_cases.request_delete.irequest_delete_use_case import (
    IRequestDeleteUseCase,
)
from src.modules.auth.public.user_id import UserId
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class RequestDeleteController(IControllerInterface):
    def __init__(self, request_delete_use_case: IRequestDeleteUseCase) -> None:
        self.__use_case = request_delete_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()

        await self.__use_case.execute(UserId(request.authenticated_user_id))
        return HttpResponse(
            status_code=202,
            body={"message": "An account deletion confirmation email has been sent."},
        )
