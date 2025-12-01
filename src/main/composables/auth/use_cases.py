from src.application.use_cases.login.login_use_case_impl import LoginUseCaseImpl
from src.application.use_cases.logoff.logoff_use_case_impl import LogoffUseCaseImpl
from src.application.use_cases.refresh.refresh_use_case_impl import RefreshUseCaseImpl
from src.application.use_cases.signup.signup_use_case_impl import SignupUseCaseImpl
from src.main.composables.auth.services import get_auth_session_service
from src.main.composables.auth.repositories import get_user_repository, get_user_email_verification_repository
from src.main.composables.shared.security import get_password_hasher
from src.main.composables.shared.system import get_clock, get_ulid_generator, get_jti_hasher
from src.main.composables.auth.services import get_email_verification_service
from src.application.use_cases.verify_email.verify_email_verification_use_case_impl import VerifyEmailVerificationUseCaseImpl

def get_login_use_case() -> LoginUseCaseImpl:
    """ Retorna uma instância do caso de uso de login com todas as dependências injetadas."""

    return LoginUseCaseImpl(
        get_user_repository(),
        get_password_hasher(),
        get_clock(),
        get_auth_session_service(),
        get_email_verification_service()
    )


def get_logoff_use_case() -> LogoffUseCaseImpl:
    """ Retorna uma instância do caso de uso de logoff com todas as dependências injetadas."""


    return LogoffUseCaseImpl(
        get_auth_session_service()
    )


def get_refresh_use_case() -> RefreshUseCaseImpl:

    return RefreshUseCaseImpl(
        get_auth_session_service(),
        get_user_repository(),
        get_clock()
    )


def get_sign_up_use_case() -> SignupUseCaseImpl:

    return SignupUseCaseImpl(
        get_user_repository(),
        get_password_hasher(),
        get_clock(),
        get_ulid_generator(),
        get_jti_hasher(),
        get_email_verification_service()
    )

def get_verify_email_use_case() -> VerifyEmailVerificationUseCaseImpl:


    return VerifyEmailVerificationUseCaseImpl(
       get_user_email_verification_repository(),
        get_jti_hasher(),
        get_email_verification_service(),
        get_user_repository(),
        get_clock()
    )
