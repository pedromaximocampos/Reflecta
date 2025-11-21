from src.presentation.controllers.auth.login_controller import LoginController

from src.main.composables.auth.use_cases import get_login_use_case


def get_login_controller() -> LoginController:
    """ Retorna uma instância do LoginController com suas dependências injetadas. """

    return LoginController(
    get_login_use_case(),
    )