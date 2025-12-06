import pytest
from unittest.mock import AsyncMock, MagicMock, Mock

from tests.support.contexts import LoginTestContext

from src.application.use_cases.login.login_use_case_impl import LoginUseCaseImpl
from src.application.use_cases.login import LoginInput


@pytest.fixture
def login_use_case_with_mocks(
    mock_user_repository,
    mock_password_hasher,
    mock_system_clock,
    mock_auth_session_service,
    mock_email_verification_service,
) -> LoginUseCaseImpl:
    return LoginUseCaseImpl(
        user_repository=mock_user_repository,
        password_hasher=mock_password_hasher,
        system_clock=mock_system_clock,
        auth_session_service=mock_auth_session_service,
        email_verification_service=mock_email_verification_service,
    )


@pytest.fixture
def login_input(mock_user):
    return LoginInput(
        email=mock_user.email,
        password="password123",
    )


@pytest.fixture
def login_ctx(
    login_use_case_with_mocks: LoginUseCaseImpl,
    mock_user_repository: AsyncMock,
    mock_password_hasher: MagicMock,
    mock_system_clock: Mock,
    mock_auth_session_service: AsyncMock,
    mock_email_verification_service: AsyncMock,
    mock_user: Mock,
) -> LoginTestContext:
    ctx = LoginTestContext(
        use_case=login_use_case_with_mocks,
        user_repo=mock_user_repository,
        password_hasher=mock_password_hasher,
        clock=mock_system_clock,
        auth_session_service=mock_auth_session_service,
        email_verification_service=mock_email_verification_service,
        user=mock_user,
    )
    # Alias para compatibilidade com testes existentes
    ctx.auth_session = mock_auth_session_service
    ctx.email_verification = mock_email_verification_service
    return ctx
