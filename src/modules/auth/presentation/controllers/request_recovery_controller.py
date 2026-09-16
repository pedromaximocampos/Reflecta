from src.modules.auth.application.use_cases.request_recovery.irequest_recovery_use_case import (
    IRequestRecoveryUseCase,
)
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class RequestRecoveryController(IControllerInterface):
    def __init__(self, request_recovery_use_case: IRequestRecoveryUseCase) -> None:
        self.__use_case = request_recovery_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        body = request.body
        email = body.email if hasattr(body, "email") else body.get("email")
        await self.__use_case.execute(str(email))
        return HttpResponse(
            status_code=202,
            body={
                "message": (
                    "If a deleted account is associated with this email, "
                    "a recovery link has been sent."
                )
            },
        )
