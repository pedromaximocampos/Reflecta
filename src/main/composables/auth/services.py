from src.application.services.auth_session.auth_session_service_impl import AuthSessionServiceImpl
from src.application.services.email_verification.email_verification_service_impl import EmailVerificationServiceImpl
from src.main.composables.auth.publishers import get_email_verification_publisher, get_email_password_reset_publisher
from src.main.composables.shared.system import get_clock, get_ulid_generator, get_jti_hasher
from src.main.composables.shared.security import get_token_service
from src.application.services.reset_password_service.password_reset_service_impl import PasswordResetServiceImpl

def get_auth_session_service() -> AuthSessionServiceImpl:
    """ Retorna a implementação do serviço de sessão de autenticação. """

    return AuthSessionServiceImpl(
        get_clock(),
        get_token_service(),
        get_ulid_generator(),
        get_jti_hasher()
    )

def get_email_verification_service() -> EmailVerificationServiceImpl:
    """ Retorna a implementação do serviço de sessão de autenticação. """

    return EmailVerificationServiceImpl(
        get_jti_hasher(),
        get_clock(),
        get_ulid_generator(),
        get_email_verification_publisher()
    )


def get_password_reset_service():

    return PasswordResetServiceImpl(
        get_email_password_reset_publisher(),
        get_clock(),
        get_ulid_generator(),
        get_jti_hasher(),
    )