from src.presentation.controllers.auth.login_controller import LoginController
from src.presentation.controllers.auth.logoff_controller import LogoffController
from src.main.composables.auth.use_cases import get_login_use_case, get_logoff_use_case, get_refresh_use_case
from src.main.composables.shared.system import get_clock
from src.presentation.controllers.auth.refresh_controller import RefreshController


def get_login_controller() -> LoginController:
    """ Retorna uma instância do LoginController com suas dependências injetadas. """

    return LoginController(
    get_login_use_case(),
    get_clock()
    )


def get_logoff_controller() -> LogoffController:
    """ Retorna uma instância do LogoffController com suas dependências injetadas. """

    return LogoffController(
    get_logoff_use_case(),
    )

def get_refresh_controller() -> RefreshController:
    """ Retorna uma instância do RefreshController com suas dependências injetadas. """

    return RefreshController(
        get_refresh_use_case(),
        get_clock()
    )