from src.presentation.controllers.auth.login_controller import LoginController
from src.presentation.controllers.auth.logoff_controller import LogoffController
from src.main.composables.auth.use_cases import get_login_use_case, get_logoff_use_case


def get_login_controller() -> LoginController:
    """ Retorna uma instância do LoginController com suas dependências injetadas. """

    return LoginController(
    get_login_use_case(),
    )


def get_logoff_controller() -> LogoffController:
    """ Retorna uma instância do LogoffController com suas dependências injetadas. """

    return LogoffController(
    get_logoff_use_case(),
    )