from src.modules.auth.application.use_cases.update_user_info.dto import UpdateUserInfoInput
from src.modules.auth.application.use_cases.update_user_info.iupdate_user_info_use_case import (
    IUpdateUserInfoUseCase,
)
from src.modules.auth.public.user_id import UserId
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


class UpdateUserInfoController(IControllerInterface):
    def __init__(self, update_user_info_use_case: IUpdateUserInfoUseCase) -> None:
        self.__use_case = update_user_info_use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()

        body = request.body
        if hasattr(body, "model_dump"):
            payload = body.model_dump(exclude_unset=True)
        else:
            payload = dict(body or {})

        avatar_url = payload.get("avatar_url")
        if avatar_url is not None:
            avatar_url = str(avatar_url)

        output = await self.__use_case.execute(
            UpdateUserInfoInput(
                user_id=UserId(request.authenticated_user_id),
                name=payload.get("name"),
                surname=payload.get("surname"),
                date_of_birth=payload.get("date_of_birth"),
                avatar_url=avatar_url,
            )
        )
        return HttpResponse(
            status_code=200,
            body={
                "user_id": output.user_id.value,
                "name": output.name,
                "surname": output.surname,
                "date_of_birth": output.date_of_birth.isoformat(),
                "avatar_url": output.avatar_url,
            },
        )
