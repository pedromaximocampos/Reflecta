from src.infra.postgresql.mappers.auth_credentials_mapper import AuthCredentialsMapper
from src.infra.postgresql.provider import individuum_mvp_provider
from src.infra.postgresql.mappers.reset_password_mapper import ResetPasswordMapper
from src.infra.postgresql.mappers.user_mapper import UserMapper
from src.infra.postgresql.mappers.email_verification_mapper import EmailVerificationMapper
from src.infra.postgresql.mappers.auth_sessions_mapper import AuthSessionsMapper
from src.infra.postgresql.units_of_work.auth_unit_of_work_impl import AuthUnitOfWorkImpl
from src.main.composables.shared.system import get_clock

def get_auth_unit_of_work() -> AuthUnitOfWorkImpl:
    """ Retorna a implementação da unidade de trabalho de autenticação. """


    return AuthUnitOfWorkImpl(
        db=individuum_mvp_provider,
        system_clock=get_clock(),
        user_mapper=UserMapper(AuthCredentialsMapper()),
        email_verification_mapper=EmailVerificationMapper(),
        auth_session_mapper=AuthSessionsMapper(),
        reset_password_mapper=ResetPasswordMapper()
    )