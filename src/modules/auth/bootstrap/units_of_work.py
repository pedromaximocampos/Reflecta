from src.modules.auth.infrastructure.persistence.postgresql.mappers.auth_credentials_mapper import AuthCredentialsMapper
from src.modules.internal_events.infrastructure.persistence.postgresql.mappers.outbox_mapper import OutboxMapper
from src.shared.infrastructure.persistence.postgresql.provider import individuum_mvp_provider
from src.modules.auth.infrastructure.persistence.postgresql.mappers.reset_password_mapper import ResetPasswordMapper
from src.modules.auth.infrastructure.persistence.postgresql.mappers.user_mapper import UserMapper
from src.modules.auth.infrastructure.persistence.postgresql.mappers.email_verification_mapper import EmailVerificationMapper
from src.modules.auth.infrastructure.persistence.postgresql.mappers.auth_sessions_mapper import AuthSessionsMapper
from src.modules.auth.infrastructure.persistence.postgresql.mappers.user_deletion_request_mapper import (
    UserDeletionRequestMapper,
)
from src.modules.auth.infrastructure.persistence.postgresql.mappers.user_recovery_request_mapper import (
    UserRecoveryRequestMapper,
)
from src.modules.auth.infrastructure.persistence.postgresql.units_of_work.auth_unit_of_work_impl import AuthUnitOfWorkImpl
from src.shared.infrastructure.system.providers import get_clock

def get_auth_unit_of_work() -> AuthUnitOfWorkImpl:
    """ Retorna a implementação da unidade de trabalho de autenticação. """


    return AuthUnitOfWorkImpl(
        db=individuum_mvp_provider,
        system_clock=get_clock(),
        user_mapper=UserMapper(AuthCredentialsMapper()),
        email_verification_mapper=EmailVerificationMapper(),
        auth_session_mapper=AuthSessionsMapper(),
        reset_password_mapper=ResetPasswordMapper(),
        user_deletion_request_mapper=UserDeletionRequestMapper(),
        user_recovery_request_mapper=UserRecoveryRequestMapper(),
        outbox_mapper=OutboxMapper(),
    )
