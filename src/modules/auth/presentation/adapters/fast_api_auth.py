from collections.abc import Awaitable, Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.bootstrap.fast_api_services import get_fast_api_auth_service
from src.modules.auth.presentation.services.fast_api_auth_service import FastAPIAuthService


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    auth_service: FastAPIAuthService = Depends(get_fast_api_auth_service),
) -> AuthenticatedPrincipal:
    return await auth_service.authenticate_request(credentials)


def require_role(
    required_role: UserRole,
) -> Callable[..., Awaitable[AuthenticatedPrincipal]]:
    async def dependency(
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
        auth_service: FastAPIAuthService = Depends(get_fast_api_auth_service),
    ) -> AuthenticatedPrincipal:
        return await auth_service.authenticate_user_role(
            credentials,
            required_role,
        )

    return dependency
