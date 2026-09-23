import pytest
from unittest.mock import AsyncMock, MagicMock, Mock
from datetime import datetime, timezone

from src.modules.auth.application.services.auth_session import IAuthSessionService
from src.modules.auth.application.services.email_verification.iemail_verification_service import IEmailVerificationService
from src.modules.auth.domain.ports.repositories.iuser_repository import IUserRepository
from src.modules.auth.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.modules.internal_events.public import IOutboxService
from tests.support.utils.id_utils import new_id as gen_id

from src.modules.auth.domain.entities.user import User, AuthCredentials
from src.modules.auth.domain.entities.auth_session import AuthSession
from src.modules.auth.public.email import Email
from src.modules.auth.domain.value_objects.password_hash import PasswordHash
from src.modules.auth.public.user_id import UserId


# ---------- helpers simples ---------- #

@pytest.fixture
def new_id() -> str:
    return gen_id()


# ---------- Repository mocks ---------- #

@pytest.fixture
def mock_user_repository():
    return AsyncMock(spec=IUserRepository)
    # se quiser depois: AsyncMock(spec=IUserRepository)


# ---------- Infra mocks ---------- #

@pytest.fixture
def mock_password_hasher():
    return MagicMock(spec=IPasswordHasher)



@pytest.fixture
def mock_system_clock():
    mock = Mock()
    mock.now.return_value = datetime.now(timezone.utc)
    return mock


# ---------- Application service mocks ---------- #

@pytest.fixture
def mock_auth_session_service():
    return AsyncMock(spec=IAuthSessionService)



@pytest.fixture
def mock_email_verification_service():
    return AsyncMock(spec=IEmailVerificationService)


@pytest.fixture
def mock_outbox_service():
    return AsyncMock(spec=IOutboxService)


@pytest.fixture
def mock_auth_unit_of_work(mock_user_repository):
    uow = MagicMock(spec=IAuthUnitOfWork)
    uow.users_repository = mock_user_repository
    uow.user_email_verification_repository = AsyncMock()
    uow.outbox_repository = AsyncMock()
    uow.commit = AsyncMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    return uow



@pytest.fixture
def mock_auth_session(new_id):
    mock = Mock(spec=AuthSession)
    mock.id = new_id
    mock.refresh_token = "test_refresh_token"
    return mock


# ---------- Domain Entity / VO mocks ---------- #

@pytest.fixture
def mock_password_hash():
    return Mock(
        spec=PasswordHash,
        algorithm="argon2",
        hash="hashed_password",
        version=1,
    )


@pytest.fixture
def mock_email():
    return Email("user@example.com")


@pytest.fixture
def mock_auth_credentials(mock_password_hash):
    mock = Mock(spec=AuthCredentials)
    mock.password = mock_password_hash
    return mock


@pytest.fixture
def mock_user_id(new_id):
    return UserId(new_id)


@pytest.fixture
def mock_user(mock_email, mock_auth_credentials, mock_user_id):
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
    mock_user.is_email_verified = False
    return mock_user
