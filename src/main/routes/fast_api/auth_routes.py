from fastapi import APIRouter, Request, Query
from src.main.adapters.fast_api.fast_api_adapter import adapter_fastapi_request
from src.main.composables.auth.controllers import get_login_controller, get_logoff_controller, get_refresh_controller, \
    get_signup_controller, get_email_verification_controller, get_reset_password_controller
from src.main.validators.fast_api.auth.login import LoginRequestValidator, LoginResponseValidator
from src.main.validators.fast_api.auth.reset_password import ResetPasswordValidator
from src.main.validators.fast_api.auth.sign_up import SignUpValidator

auth_router = APIRouter(prefix="/auth", tags=["auth"])


_LOGIN_CONTROLLER = get_login_controller()
_LOGOFF_CONTROLLER = get_logoff_controller()
_REFRESH_CONTROLLER = get_refresh_controller()
_SIGNUP_CONTROLLER = get_signup_controller()
_VALIDATE_EMAIL_CONTROLLER = get_email_verification_controller()
_RESET_PASSWORD_CONTROLLER = get_reset_password_controller()


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
async def auth_reset_password(body: ResetPasswordValidator,  request: Request):
    """ Auth User reset password endpoint"""
    return await adapter_fastapi_request(request, _RESET_PASSWORD_CONTROLLER.handle_request, body)