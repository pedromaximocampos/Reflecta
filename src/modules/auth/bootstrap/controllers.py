from src.modules.auth.presentation.controllers.login_controller import LoginController
from src.modules.auth.presentation.controllers.logoff_controller import LogoffController
from src.modules.auth.bootstrap.use_cases import get_login_use_case, get_logoff_use_case, get_refresh_use_case, \
    get_sign_up_use_case, get_verify_email_use_case, get_reset_password_use_case, get_request_password_reset_use_case
from src.main.composables.shared.system import get_clock
from src.modules.auth.presentation.controllers.refresh_controller import RefreshController
from src.modules.auth.presentation.controllers.request_reset_password_controller import RequestResetPasswordController
from src.modules.auth.presentation.controllers.reset_password_controller import ResetPasswordController
from src.modules.auth.presentation.controllers.sign_up_controller import SignUpController
from src.modules.auth.presentation.controllers.verify_email_controller import VerifyEmailController


def get_login_controller() -> LoginController:
    """ Retorna uma instância do LoginController com suas dependências injetadas. """

    return LoginController(
    login_use_case=get_login_use_case(),
    system_clock=get_clock()
    )


def get_logoff_controller() -> LogoffController:
    """ Retorna uma instância do LogoffController com suas dependências injetadas. """

    return LogoffController(
    logoff_use_case=get_logoff_use_case(),
    )

def get_refresh_controller() -> RefreshController:
    """ Retorna uma instância do RefreshController com suas dependências injetadas. """

    return RefreshController(
        refresh_use_case=get_refresh_use_case(),
        system_clock=get_clock()
    )

def get_signup_controller():
    """ Retorna uma instância do SignupController com suas dependências injetadas. """

    return SignUpController(
        sign_up_use_case=get_sign_up_use_case(),
    )

def get_email_verification_controller():
    """ Retorna uma instância do EmailVerificationController com suas dependências injetadas. """

    return VerifyEmailController(
        verify_email_use_case=get_verify_email_use_case(),
    )


def get_reset_password_controller():
    """ Retorna uma instância do caso de uso de redefinição de senha com todas as dependências injetadas."""

    return ResetPasswordController(
        reset_password_use_case=get_reset_password_use_case()
    )

def get_request_reset_password_controller():
    """ Retorna uma instância do caso de uso de solicitação de redefinição de senha com todas as dependências injetadas."""

    return RequestResetPasswordController(
        request_reset_password_use_case=get_request_password_reset_use_case()
    )