import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
from datetime import datetime,  timezone
from src.domain.entities.auth_session import AuthSession
from src.domain.entities.user import User, AuthCredentials
from src.domain.value_objects.email import Email
from src.domain.value_objects.password_hash import PasswordHash
from src.domain.value_objects.user_id import UserId

# Repository Mocks

@pytest.fixture
def mock_user_repository():
    return AsyncMock()


# Infra Mocks
@pytest.fixture
def mock_password_hasher():
    return MagicMock()

@pytest.fixture
def mock_system_clock():
    mock = Mock()
    mock.now.return_value = datetime.now(timezone.utc)
    return mock

# Application Service Mocks
@pytest.fixture
def mock_auth_session_service():
    return AsyncMock()

@pytest.fixture
def mock_auth_session(new_id):
    mock = Mock(spec=AuthSession)
    mock.id = new_id
    mock.refresh_token = "test_refresh_token"
    return mock

@pytest.fixture
def mock_email_verification_service():
    return AsyncMock()


# Domain Entity/VO Mocks

@pytest.fixture
def mock_password_hash():
    """Mock de PasswordHash"""
    return Mock(spec=PasswordHash, algorithm="argon2", hash="hashed_password", version=1)


@pytest.fixture
def mock_email():
    """Email padrão para testes"""
    return Email("user@example.com")


@pytest.fixture
def mock_auth_credentials(mock_password_hash):

    mock = Mock(spec=AuthCredentials)
    mock.password = mock_password_hash
    return mock

@pytest.fixture
def mock_user_id(new_id):
    """Mock de UserId"""

    return UserId(new_id)

@pytest.fixture
def mock_user(mock_email, mock_auth_credentials, mock_user_id):
    """Mock de User com configuração padrão"""
    mock = Mock(spec=User)
    mock.id = mock_user_id
    mock.email = mock_email
    mock.name = "John"
    mock.surname = "Doe"
    mock.username = "johndoe"
    mock.avatar_url = None
    mock.is_email_verified = True
    mock.auth_credentials = mock_auth_credentials
    mock.last_login_at = None
    mock.update_auth_credentials = Mock()
    mock.update_last_login = Mock()
    return mock

@pytest.fixture
def mock_user_unverified(mock_user):
    """Mock de User com email não verificado"""
    mock_user.is_email_verified = False
    return mock_user