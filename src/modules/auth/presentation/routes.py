from fastapi import APIRouter, Depends, Request, Query
from src.modules.auth.application.services.http_request_auth.dto import AuthenticatedUserDTO
from src.modules.auth.presentation.adapters.fast_api_auth import get_current_user
from src.shared.presentation.fast_api.fast_api_adapter import adapter_fastapi_request
from src.modules.auth.bootstrap.controllers import (
    get_delete_user_controller,
    get_email_verification_controller,
    get_login_controller,
    get_logoff_controller,
    get_refresh_controller,
    get_request_delete_controller,
    get_request_recovery_controller,
    get_recovery_controller,
    get_request_reset_password_controller,
    get_reset_password_controller,
    get_signup_controller,
    get_update_user_info_controller,
)
from src.modules.auth.presentation.validators.login import LoginResponseValidator
from src.modules.auth.presentation.validators.sign_up import SignUpValidator
from src.modules.auth.presentation.validators.recovery import RequestRecoveryValidator
from src.modules.auth.presentation.validators.update_user_info import (
    UpdateUserInfoResponseValidator,
    UpdateUserInfoValidator,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


_LOGIN_CONTROLLER = get_login_controller()
_LOGOFF_CONTROLLER = get_logoff_controller()
_REFRESH_CONTROLLER = get_refresh_controller()
_SIGNUP_CONTROLLER = get_signup_controller()
_VALIDATE_EMAIL_CONTROLLER = get_email_verification_controller()
_RESET_PASSWORD_CONTROLLER = get_reset_password_controller()
_REQUEST_PASSWORD_RESET_CONTROLLER = get_request_reset_password_controller()
_REQUEST_DELETE_CONTROLLER = get_request_delete_controller()
_DELETE_USER_CONTROLLER = get_delete_user_controller()
_REQUEST_RECOVERY_CONTROLLER = get_request_recovery_controller()
_RECOVERY_CONTROLLER = get_recovery_controller()
_UPDATE_USER_INFO_CONTROLLER = get_update_user_info_controller()


@auth_router.post("/login", response_model=LoginResponseValidator)
async def auth_login(request:  Request):
    """ Auth User login endpoint"""
    return await adapter_fastapi_request(request, _LOGIN_CONTROLLER.handle_request)


@auth_router.post("/logoff")
async def auth_logoff(request:  Request):
    """ Auth User logoff endpoint"""
    return await adapter_fastapi_request(request, _LOGOFF_CONTROLLER.handle_request)


@auth_router.post("/refresh", response_model=LoginResponseValidator)
async def auth_refresh(request:  Request):
    """ Auth User token refresh endpoint"""
    return await adapter_fastapi_request(request, _REFRESH_CONTROLLER.handle_request)


@auth_router.post("/signup")
async def auth_signup(body: SignUpValidator, request:  Request):
    """ Auth User signup endpoint"""
    return await adapter_fastapi_request(request, _SIGNUP_CONTROLLER.handle_request, body)

@auth_router.get("/verify-email")
async def auth_verify_email(
    code: str = Query(..., description="Verification code sent to the user email"),
    request: Request = None,
):
    """ Auth User email verification endpoint"""
    return await adapter_fastapi_request(request, _VALIDATE_EMAIL_CONTROLLER.handle_request)


@auth_router.post("/reset-password")
async def auth_reset_password(request: Request):
    """ Auth User reset password endpoint"""
    return await adapter_fastapi_request(request, _RESET_PASSWORD_CONTROLLER.handle_request)


@auth_router.post("/request-reset-password")
async def auth_request_reset_password(request: Request):
    """ Auth User request reset password endpoint"""
    return await adapter_fastapi_request(request, _REQUEST_PASSWORD_RESET_CONTROLLER.handle_request)


@auth_router.post("/request-delete", status_code=202)
async def auth_request_delete(
    request: Request,
    current_user: AuthenticatedUserDTO = Depends(get_current_user),
):
    """Request a one-time account deletion confirmation code."""
    return await adapter_fastapi_request(
        request,
        _REQUEST_DELETE_CONTROLLER.handle_request,
        authenticated_user_id=current_user.user_id.value,
    )


@auth_router.delete("/delete")
async def auth_delete_user(
    request: Request,
    code: str = Query(..., description="Account deletion code sent to the user email"),
):
    """Confirm a logical account deletion using a one-time code."""
    return await adapter_fastapi_request(request, _DELETE_USER_CONTROLLER.handle_request)


@auth_router.post("/request-recovery", status_code=202)
async def auth_request_recovery(body: RequestRecoveryValidator, request: Request):
    """Request recovery without revealing whether a deleted account exists."""
    return await adapter_fastapi_request(
        request,
        _REQUEST_RECOVERY_CONTROLLER.handle_request,
        body,
    )


@auth_router.post("/recovery")
async def auth_recovery(
    request: Request,
    code: str = Query(..., description="Account recovery code sent to the user email"),
):
    """Recover a logically deleted account using a one-time code."""
    return await adapter_fastapi_request(request, _RECOVERY_CONTROLLER.handle_request)


@auth_router.patch("/user-info", response_model=UpdateUserInfoResponseValidator)
async def auth_update_user_info(
    body: UpdateUserInfoValidator,
    request: Request,
    current_user: AuthenticatedUserDTO = Depends(get_current_user),
):
    """Update one or more allowed fields of the authenticated user's profile."""
    return await adapter_fastapi_request(
        request,
        _UPDATE_USER_INFO_CONTROLLER.handle_request,
        body,
        authenticated_user_id=current_user.user_id.value,
    )
