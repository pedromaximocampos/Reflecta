from src.application.services.auth.auth_session.auth_session_service_impl import AuthSessionServiceImpl
from src.application.services.auth.email_verification.email_verification_service_impl import EmailVerificationServiceImpl
from src.main.composables.shared.services import get_outbox_service
from src.main.composables.shared.system import get_clock, get_ulid_generator, get_jti_hasher
from src.main.composables.shared.security import get_token_service
from src.application.services.auth.reset_password_service.password_reset_service_impl import PasswordResetServiceImpl
from src.main.composables.shared.settings import _SETTINGS

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