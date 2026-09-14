from src.modules.auth.application.use_cases.login.login_use_case_impl import LoginUseCaseImpl
from src.modules.auth.application.use_cases.logoff.logoff_use_case_impl import LogoffUseCaseImpl
from src.modules.auth.application.use_cases.refresh.refresh_use_case_impl import RefreshUseCaseImpl
from src.modules.auth.application.use_cases.signup.signup_use_case_impl import SignupUseCaseImpl
from src.modules.auth.bootstrap.services import (
    get_auth_session_service,
    get_password_reset_service,
    get_user_deletion_service,
    get_user_recovery_service,
)
from src.modules.auth.bootstrap.units_of_work import get_auth_unit_of_work
from src.modules.auth.bootstrap.security import get_jti_hasher, get_password_hasher
from src.modules.internal_events.bootstrap.services import get_outbox_service
from src.shared.infrastructure.system.providers import get_clock, get_ulid_generator
from src.modules.auth.bootstrap.services import get_email_verification_service
from src.modules.auth.application.use_cases.verify_email.verify_email_verification_use_case_impl import VerifyEmailVerificationUseCaseImpl
from src.modules.auth.application.use_cases.reset_password.reset_password_use_case_impl import ResetPasswordUseCaseImpl
from src.modules.auth.application.use_cases.request_password_reset.request_password_reset_use_case_impl import RequestPasswordResetUseCaseImpl
from src.modules.auth.application.use_cases.request_delete.request_delete_use_case_impl import (
    RequestDeleteUseCaseImpl,
)
from src.modules.auth.application.use_cases.delete.delete_user_use_case_impl import (
    DeleteUserUseCaseImpl,
)
from src.modules.auth.application.use_cases.request_recovery.request_recovery_use_case_impl import (
    RequestRecoveryUseCaseImpl,
)
from src.modules.auth.application.use_cases.recovery.recovery_use_case_impl import (
    RecoveryUseCaseImpl,
)
from src.modules.auth.application.use_cases.update_user_info.update_user_info_use_case_impl import (
    UpdateUserInfoUseCaseImpl,
)

def get_login_use_case() -> LoginUseCaseImpl:
    """ Retorna uma instância do caso de uso de login com todas as dependências injetadas."""

    return LoginUseCaseImpl(
        password_hasher=get_password_hasher(),
        system_clock=get_clock(),
        auth_session_service=get_auth_session_service(),
        email_verification_service=get_email_verification_service(),
        auth_unit_of_work=get_auth_unit_of_work(),
        outbox_service=get_outbox_service()
    )


def get_logoff_use_case() -> LogoffUseCaseImpl:
    """ Retorna uma instância do caso de uso de logoff com todas as dependências injetadas."""


    return LogoffUseCaseImpl(
        get_auth_session_service(),
        auth_unit_of_work=get_auth_unit_of_work()
    )


def get_refresh_use_case() -> RefreshUseCaseImpl:

    return RefreshUseCaseImpl(
        auth_session_service=get_auth_session_service(),
        auth_unit_of_work=get_auth_unit_of_work(),
        system_clock=get_clock()
    )


def get_sign_up_use_case() -> SignupUseCaseImpl:

    return SignupUseCaseImpl(
        auth_unit_of_work=get_auth_unit_of_work(),
        password_hasher=get_password_hasher(),
        system_clock=get_clock(),
        ulid_generator=get_ulid_generator(),
        hash_generator=get_jti_hasher(),
        email_verification_service=get_email_verification_service(),
        outbox_service=get_outbox_service()
    )

def get_verify_email_use_case() -> VerifyEmailVerificationUseCaseImpl:


    return VerifyEmailVerificationUseCaseImpl(
        auth_unit_of_work=get_auth_unit_of_work(),
        hasher_generator=get_jti_hasher(),
        email_verification_service=get_email_verification_service(),
        system_clock=get_clock(),
        outbox_service=get_outbox_service()
    )



def get_reset_password_use_case() -> ResetPasswordUseCaseImpl:


    return ResetPasswordUseCaseImpl(
        system_clock=get_clock(),
        auth_unit_of_work=get_auth_unit_of_work(),
        hasher_generator=get_jti_hasher(),
        password_hasher=get_password_hasher(),
        auth_sessions_service=get_auth_session_service(),
    )

def get_request_password_reset_use_case() -> RequestPasswordResetUseCaseImpl:


    return RequestPasswordResetUseCaseImpl (
        auth_unit_of_work=get_auth_unit_of_work(),
        password_reset_service=get_password_reset_service(),
        system_clock=get_clock(),
        outbox_service=get_outbox_service()
    )


def get_request_delete_use_case() -> RequestDeleteUseCaseImpl:
    return RequestDeleteUseCaseImpl(
        auth_unit_of_work=get_auth_unit_of_work(),
        user_deletion_service=get_user_deletion_service(),
        outbox_service=get_outbox_service(),
    )


def get_delete_user_use_case() -> DeleteUserUseCaseImpl:
    return DeleteUserUseCaseImpl(
        auth_unit_of_work=get_auth_unit_of_work(),
        hasher_generator=get_jti_hasher(),
        system_clock=get_clock(),
        auth_session_service=get_auth_session_service(),
        outbox_service=get_outbox_service(),
    )


def get_request_recovery_use_case() -> RequestRecoveryUseCaseImpl:
    return RequestRecoveryUseCaseImpl(
        auth_unit_of_work=get_auth_unit_of_work(),
        user_recovery_service=get_user_recovery_service(),
        outbox_service=get_outbox_service(),
    )


def get_recovery_use_case() -> RecoveryUseCaseImpl:
    return RecoveryUseCaseImpl(
        auth_unit_of_work=get_auth_unit_of_work(),
        hasher_generator=get_jti_hasher(),
        system_clock=get_clock(),
        outbox_service=get_outbox_service(),
    )


def get_update_user_info_use_case() -> UpdateUserInfoUseCaseImpl:
    return UpdateUserInfoUseCaseImpl(
        auth_unit_of_work=get_auth_unit_of_work(),
        system_clock=get_clock(),
    )
