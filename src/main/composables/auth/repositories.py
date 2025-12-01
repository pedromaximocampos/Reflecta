# Mappers
from src.infra.postgresql.mappers.user_mapper import UserMapper
from src.infra.postgresql.mappers.auth_sessions_mapper import AuthSessionsMapper
from src.infra.postgresql.mappers.email_verification_mapper import EmailVerificationMapper
# Providers
from src.infra.postgresql.provider import individuum_mvp_provider

# Repositories
from src.infra.postgresql.repositories.auth_sessions_repository import AuthSessionsRepository
from src.infra.postgresql.repositories.user_email_verification_repository import UserEmailVerificationRepository
from src.infra.postgresql.repositories.user_repository import UserRepository

from src.main.composables.shared.system import get_clock

_USER_MAPPER = UserMapper()
_AUTH_SESSIONS_MAPPER = AuthSessionsMapper()
_USER_EMAIL_VERIFICATION_MAPPER = EmailVerificationMapper()

def get_user_repository() -> UserRepository:
    """ Retorna uma instância do UserRepository com o mapper apropriado """
    return UserRepository(individuum_mvp_provider, _USER_MAPPER)


def get_auth_sessions_repository() -> AuthSessionsRepository:
    """ Retorna uma instância do AuthSessionsRepository com o mapper apropriado """
    return AuthSessionsRepository(individuum_mvp_provider, _AUTH_SESSIONS_MAPPER, get_clock())

def get_user_email_verification_repository() -> UserEmailVerificationRepository:
    return UserEmailVerificationRepository(individuum_mvp_provider, _USER_EMAIL_VERIFICATION_MAPPER)