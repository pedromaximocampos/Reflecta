from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from src.modules.auth.presentation.services.fast_api_auth_service import (
    FastAPIAuthService,
)
from src.modules.auth.public import AuthenticatedPrincipal, UserId, UserRole
from tests.support.utils.id_utils import new_id


def credentials() -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="access-token",
    )


@pytest.mark.asyncio
async def test_authenticate_user_role_returns_admin_principal() -> None:
    principal = AuthenticatedPrincipal(
        user_id=UserId(new_id()),
        role=UserRole.ADMIN,
    )
    authenticate_request_service = AsyncMock()
    authenticate_request_service.authenticate_request.return_value = principal
    service = FastAPIAuthService(authenticate_request_service)

    result = await service.authenticate_user_role(
        credentials(),
        UserRole.ADMIN,
    )

    assert result is principal


@pytest.mark.asyncio
async def test_authenticate_user_role_rejects_principal_without_required_role() -> None:
    principal = AuthenticatedPrincipal(
        user_id=UserId(new_id()),
        role=UserRole.USER,
    )
    authenticate_request_service = AsyncMock()
    authenticate_request_service.authenticate_request.return_value = principal
    service = FastAPIAuthService(authenticate_request_service)

    with pytest.raises(HTTPException) as exc_info:
        await service.authenticate_user_role(
            credentials(),
            UserRole.ADMIN,
        )

    assert exc_info.value.status_code == 403
