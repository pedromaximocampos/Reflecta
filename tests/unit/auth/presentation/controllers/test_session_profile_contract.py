from unittest.mock import AsyncMock, Mock

import pytest
from basicauth import encode

from src.modules.auth.application.use_cases.login import LoginUseCaseImpl
from src.modules.auth.application.use_cases.refresh.dto import RefreshResultDTO
from src.modules.auth.presentation.controllers.login_controller import LoginController
from src.modules.auth.presentation.controllers.refresh_controller import RefreshController
from src.modules.auth.presentation.validators.login import LoginResponseValidator
from src.modules.auth.public import UserRole
from src.shared.presentation.http_types import HttpRequest
from tests.support.builders.user_builder import UserBuilder


@pytest.mark.asyncio
@pytest.mark.parametrize('role', [UserRole.USER, UserRole.ADMIN])
async def test_login_and_refresh_preserve_profile_and_role(role):
    user = UserBuilder().with_role(role).build()
    clock = Mock()
    clock.refresh_token_expiration_in_seconds.return_value = 3600
    session = Mock(access_token='access-token', refresh_token='refresh-token')
    login_use_case = AsyncMock()
    login_use_case.execute.return_value = LoginUseCaseImpl._LoginUseCaseImpl__create_login_output(user, session)
    refresh_use_case = AsyncMock()
    refresh_use_case.execute.return_value = RefreshResultDTO('access-token', 'refresh-token', user)

    login = await LoginController(login_use_case, clock).handle_request(HttpRequest(
        method='POST', url='/auth/login',
        headers={'authorization': encode(user.email.value, 'test-password')},
    ))
    refresh = await RefreshController(refresh_use_case, clock).handle_request(HttpRequest(
        method='POST', url='/auth/refresh', cookies={'refresh_token': 'refresh-token'},
    ))

    for response in (login, refresh):
        assert response.status_code == 200
        payload = LoginResponseValidator.model_validate(response.body).model_dump(mode='json')
        assert payload['user']['role'] == role.value
        assert payload['user']['date_of_birth'] == '2000-01-01'
        assert payload['user']['email'] == user.email.value
        assert 'refresh_token' not in payload
    assert login.body['user'] == refresh.body['user']
