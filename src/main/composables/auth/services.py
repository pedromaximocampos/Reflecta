from src.application.services.auth_session.auth_session_service_impl import AuthSessionServiceImpl
from src.application.services.email_verification.email_verification_service_impl import EmailVerificationServiceImpl
from src.main.composables.auth.repositories import get_auth_sessions_repository, get_user_email_verification_repository
from src.main.composables.auth.publishers import get_email_verification_publisher
from src.main.composables.shared.system import get_clock, get_ulid_generator, get_jti_hasher
from src.main.composables.shared.security import get_token_service

def get_auth_session_service() -> AuthSessionServiceImpl:
    """ Retorna a implementação do serviço de sessão de autenticação. """

    return AuthSessionServiceImpl(
        get_auth_sessions_repository(),
        get_clock(),
        get_token_service(),
        get_ulid_generator(),
        get_jti_hasher()
    )

def get_email_verification_service() -> EmailVerificationServiceImpl:
    """ Retorna a implementação do serviço de sessão de autenticação. """

    return EmailVerificationServiceImpl(
        get_user_email_verification_repository(),
        get_jti_hasher(),
        get_clock(),
        get_ulid_generator(),
        get_email_verification_publisher()
    )