from dataclasses import dataclass
from unittest.mock import AsyncMock, Mock, MagicMock
import pytest
from src.application.use_cases.login import LoginInput
from src.application.use_cases.login.login_use_case_impl import LoginUseCaseImpl


@dataclass
class LoginTestContext:
    use_case: LoginUseCaseImpl
    user_repo: AsyncMock
    password_hasher: MagicMock
    clock: Mock
    auth_session: AsyncMock
    email_verification: AsyncMock
    user: Mock  # Mock(spec=User)

# -------------------------------------------------------------------
# Contexto único para os testes de login
# -------------------------------------------------------------------

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
    return LoginTestContext(
        use_case=login_use_case_with_mocks,
        user_repo=mock_user_repository,
        password_hasher=mock_password_hasher,
        clock=mock_system_clock,
        auth_session=mock_auth_session_service,
        email_verification=mock_email_verification_service,
        user=mock_user,
    )


# -------------------------------------------------------------------
# Input padrão para login
# -------------------------------------------------------------------

@pytest.fixture
def login_input(mock_user: Mock) -> LoginInput:
    return LoginInput(
        email=mock_user.email,
        password="password123",
    )



@pytest.fixture
def login_use_case_with_mocks(
        mock_user_repository,
        mock_password_hasher,
        mock_system_clock,
        mock_auth_session_service,
        mock_email_verification_service
):

    return LoginUseCaseImpl(
        user_repository=mock_user_repository,
        password_hasher=mock_password_hasher,
        system_clock=mock_system_clock,
        auth_session_service=mock_auth_session_service,
        email_verification_service=mock_email_verification_service
    )
