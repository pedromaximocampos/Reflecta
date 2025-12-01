from src.presentation.controllers.auth.login_controller import LoginController
from src.presentation.controllers.auth.logoff_controller import LogoffController
from src.main.composables.auth.use_cases import get_login_use_case, get_logoff_use_case, get_refresh_use_case, \
    get_sign_up_use_case, get_verify_email_use_case
from src.main.composables.shared.system import get_clock
from src.presentation.controllers.auth.refresh_controller import RefreshController
from src.presentation.controllers.auth.sign_up_controller import SignUpController
from src.presentation.controllers.auth.verify_email_controller import VerifyEmailController


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

def get_signup_controller():
    """ Retorna uma instância do SignupController com suas dependências injetadas. """

    return SignUpController(
        get_sign_up_use_case(),
    )

def get_email_verification_controller():
    """ Retorna uma instância do EmailVerificationController com suas dependências injetadas. """

    return VerifyEmailController(
        get_verify_email_use_case(),
    )
