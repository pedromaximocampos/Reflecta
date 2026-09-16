from unittest.mock import AsyncMock, MagicMock

import pytest

from src.modules.auth.application.services.http_request_auth.authenticate_request_service_impl import (
    AuthenticateRequestServiceImpl,
)
from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from tests.support.builders.user_builder import UserBuilder


@pytest.mark.asyncio
@pytest.mark.parametrize("role", [UserRole.USER, UserRole.ADMIN])
async def test_authenticate_request_returns_principal_with_persisted_role(
    role: UserRole,
) -> None:
    user = UserBuilder().with_role(role).build()
    token_service = MagicMock()
    token_service.validate_token.return_value = {"sub": user.id.value}

    users_repository = MagicMock()
    users_repository.find_by_id = AsyncMock(return_value=user)
    unit_of_work = MagicMock()
    unit_of_work.users_repository = users_repository
    unit_of_work.__aenter__ = AsyncMock(return_value=unit_of_work)
    unit_of_work.__aexit__ = AsyncMock(return_value=None)

    service = AuthenticateRequestServiceImpl(token_service, unit_of_work)

    principal = await service.authenticate_request("access-token")

    assert principal == AuthenticatedPrincipal(user_id=user.id, role=role)
    assert principal.is_admin is (role is UserRole.ADMIN)
    users_repository.find_by_id.assert_awaited_once_with(user.id)
