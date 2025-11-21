from src.application.use_cases.login.login_use_case_impl import LoginUseCaseImpl

from src.main.composables.auth.services import get_auth_session_service
from src.main.composables.auth.repositories import get_user_repository
from src.main.composables.shared.security import get_password_hasher
from src.main.composables.shared.system import get_clock


def get_login_use_case() -> LoginUseCaseImpl:
    """ Retorna uma instância do caso de uso de login com todas as dependências injetadas."""

    return LoginUseCaseImpl(
        get_user_repository(),
        get_password_hasher(),
        get_clock(),
        get_auth_session_service()
    )