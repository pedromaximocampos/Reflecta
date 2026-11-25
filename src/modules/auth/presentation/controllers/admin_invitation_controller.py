from src.modules.auth.application.use_cases.admin_invitations import AdminInvitationUseCases
from src.modules.auth.domain.exceptions.admin_invitation_exceptions import (
    AdminInvitationTokenError,
)
from src.shared.presentation.http_types import HttpRequest, HttpResponse


class AdminInvitationController:
    def __init__(self, use_cases: AdminInvitationUseCases) -> None:
        self.__use_cases = use_cases

    async def invite(self, request: HttpRequest) -> HttpResponse:
        invitation = await self.__use_cases.invite(
            request.body.email,
            request.authenticated_user_id,
        )
        return HttpResponse(status_code=202, body={"invitation": invitation})

    async def list(self, request: HttpRequest) -> HttpResponse:
        invitations = await self.__use_cases.list(request.authenticated_user_id)
        return HttpResponse(
            status_code=200,
            body={"invitations": invitations, "total": len(invitations)},
        )

    async def revoke(self, request: HttpRequest) -> HttpResponse:
        invitation = await self.__use_cases.revoke(
            request.path_params["invitation_id"],
            request.authenticated_user_id,
        )
        return HttpResponse(status_code=200, body={"invitation": invitation})

    async def accept(self, request: HttpRequest) -> HttpResponse:
        code = request.query_params.get("code")
        if not isinstance(code, str) or not code.strip():
            raise AdminInvitationTokenError()
        result = await self.__use_cases.accept(code, request.authenticated_user_id)
        return HttpResponse(status_code=200, body=result)
