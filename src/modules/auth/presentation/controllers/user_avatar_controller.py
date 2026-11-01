from src.modules.auth.application.use_cases.get_user_profile import (
    IGetUserProfileUseCase,
)
from src.modules.auth.application.use_cases.update_user_avatar import (
    IRemoveUserAvatarUseCase,
    IReplaceUserAvatarUseCase,
    RemoveUserAvatarInputDTO,
    ReplaceUserAvatarInputDTO,
)
from src.modules.auth.public.user_id import UserId
from src.shared.domain.errors.api_types import AuthError
from src.shared.presentation.http_types import HttpRequest, HttpResponse
from src.shared.presentation.interfaces.controller_interface import IControllerInterface


def _profile_response(output) -> HttpResponse:
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


class GetUserProfileController(IControllerInterface):
    def __init__(self, use_case: IGetUserProfileUseCase) -> None:
        self.__use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()
        output = await self.__use_case.execute(UserId(request.authenticated_user_id))
        return _profile_response(output)


class ReplaceUserAvatarController(IControllerInterface):
    def __init__(self, use_case: IReplaceUserAvatarUseCase) -> None:
        self.__use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()
        payload = dict(request.body or {})
        output = await self.__use_case.execute(
            ReplaceUserAvatarInputDTO(
                user_id=UserId(request.authenticated_user_id),
                content=payload["content"],
                content_type=payload["content_type"],
                size_bytes=payload["size_bytes"],
            )
        )
        return _profile_response(output)


class RemoveUserAvatarController(IControllerInterface):
    def __init__(self, use_case: IRemoveUserAvatarUseCase) -> None:
        self.__use_case = use_case

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        if request.authenticated_user_id is None:
            raise AuthError()
        output = await self.__use_case.execute(
            RemoveUserAvatarInputDTO(user_id=UserId(request.authenticated_user_id))
        )
        return _profile_response(output)
