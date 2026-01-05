from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.services.http_request_auth.dto import AuthenticatedUserDTO
from src.main.composables.fast_api.services import get_fast_api_auth_service

_FAST_API_AUTH_SERVICE = get_fast_api_auth_service()




async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> AuthenticatedUserDTO:
    return await _FAST_API_AUTH_SERVICE.authenticate_request(credentials)