from fastapi import APIRouter, Request
from src.main.adapters.fast_api.fast_api_adapter import adapter_fastapi_request
from src.main.composables.auth.controllers import get_login_controller
from src.main.validators.fast_api.auth.login import LoginRequestValidator, LoginResponseValidator

auth_router = APIRouter(prefix="/auth", tags=["auth"])


_LOGIN_CONTROLLER = get_login_controller()


@auth_router.post("/login", response_model=LoginResponseValidator)
async def auth_login(request:  Request, body: LoginRequestValidator):
    """ Auth User login endpoint"""
    return await adapter_fastapi_request(request, _LOGIN_CONTROLLER.handle_request, body.model_dump())

