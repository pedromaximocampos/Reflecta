from src.main.composables.use_cases.auth import get_auth_unit_of_work
from src.main.composables.shared.security import get_token_service
from src.main.server.fast_api.fast_api_auth_service import FastAPIAuthService
from src.application.services.auth.http_request_auth.authenticate_request_service_impl import AuthenticateRequestServiceImpl


def get_fast_api_auth_service() -> FastAPIAuthService:
    """ Retorna uma instância do FastAPIAuthService com suas dependências injetadas. """

    return FastAPIAuthService(
        get_authenticate_request_service()
    )


def get_authenticate_request_service() -> AuthenticateRequestServiceImpl:
    """ Retorna uma instância do AuthenticateRequestServiceImpl com suas dependências injetadas. """


    return AuthenticateRequestServiceImpl(
        get_token_service(),
        get_auth_unit_of_work()
    )