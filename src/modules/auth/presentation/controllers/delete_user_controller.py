from src.modules.auth.application.use_cases.delete.idelete_user_use_case import (
    IDeleteUserUseCase,
)
from src.modules.auth.domain.exceptions.user_deletion_exceptions import UserDeletionTokenError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class DeleteUserController(IControllerInterface):
    def __init__(self, delete_user_use_case: IDeleteUserUseCase) -> None:
        self.__use_case = delete_user_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        code = request.query_params.get("code")
        if not isinstance(code, str) or not code.strip():
            raise UserDeletionTokenError("Account deletion code is required.")

        await self.__use_case.execute(code)
        return HttpResponse(
            status_code=200,
            body={"message": "Account deleted successfully."},
        )
