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
        individuum_mvp_provider,
        get_clock(),
        UserMapper(),
        EmailVerificationMapper(),
        AuthSessionsMapper(),
        ResetPasswordMapper()
    )