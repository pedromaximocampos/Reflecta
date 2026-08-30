from src.modules.auth.application.services.auth_session.auth_session_service_impl import AuthSessionServiceImpl
from src.modules.auth.application.services.email_verification.email_verification_service_impl import EmailVerificationServiceImpl
from src.modules.internal_events.bootstrap.services import get_outbox_service
from src.shared.config.settings import get_settings
from src.shared.infrastructure.system.providers import get_clock, get_ulid_generator
from src.modules.auth.bootstrap.security import get_jti_hasher, get_token_service
from src.modules.auth.application.services.reset_password_service.password_reset_service_impl import PasswordResetServiceImpl

_SETTINGS = get_settings()

def get_auth_session_service() -> AuthSessionServiceImpl:
    """ Retorna a implementação do serviço de sessão de autenticação. """

    return AuthSessionServiceImpl(
        system_clock=get_clock(),
        token_service=get_token_service(),
        ulid_generator=get_ulid_generator(),
        hasher_generator=get_jti_hasher(),
        max_sessions_per_user=_SETTINGS.MAX_SESSIONS_PER_USER,

    )

def get_email_verification_service() -> EmailVerificationServiceImpl:
    """ Retorna a implementação do serviço de sessão de autenticação. """

    return EmailVerificationServiceImpl(
        hash_generator=get_jti_hasher(),
        system_clock=get_clock(),
        ulid_generator=get_ulid_generator(),
    )


def get_password_reset_service():

    return PasswordResetServiceImpl(
        system_clock=get_clock(),
        ulid_generator=get_ulid_generator(),
        hasher_generator=get_jti_hasher(),
    )
