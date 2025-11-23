from fastapi import APIRouter, Request
from src.main.adapters.fast_api.fast_api_adapter import adapter_fastapi_request
from src.main.composables.auth.controllers import get_login_controller, get_logoff_controller, get_refresh_controller
from src.main.validators.fast_api.auth.login import LoginRequestValidator, LoginResponseValidator


auth_router = APIRouter(prefix="/auth", tags=["auth"])


_LOGIN_CONTROLLER = get_login_controller()
_LOGOFF_CONTROLLER = get_logoff_controller()
_REFRESH_CONTROLLER = get_refresh_controller()


@auth_router.post("/login", response_model=LoginResponseValidator)
async def auth_login(request:  Request, body: LoginRequestValidator):
    """ Auth User login endpoint"""
    return await adapter_fastapi_request(request, _LOGIN_CONTROLLER.handle_request, body.model_dump())


@auth_router.post("/logoff")
async def auth_logoff(request:  Request):
    """ Auth User logoff endpoint"""
    return await adapter_fastapi_request(request, _LOGOFF_CONTROLLER.handle_request)


@auth_router.post("/refresh", response_model=LoginResponseValidator)
async def auth_refresh(request:  Request):
    """ Auth User token refresh endpoint"""
    return await adapter_fastapi_request(request, _REFRESH_CONTROLLER.handle_request)


@auth_router.post("/signup")
async def auth_signup():
    """ Auth User signup endpoint"""
    return {"message": "Signup endpoint - to be implemented"}