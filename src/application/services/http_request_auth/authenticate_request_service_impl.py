from iauthenticate_request_service import IAuthenticateRequestService
from src.application.services.http_request_auth.dto import AuthenticatedUserDTO
from src.application.services.token.itoken_service import ITokenService
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.exceptions.api_types import AuthError
from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.domain.value_objects.user_id import UserId



class AuthenticateRequestServiceImpl(IAuthenticateRequestService):

    def __init__(self, token_service: ITokenService, auth_unit_of_work: IAuthUnitOfWork) -> None:
        self.__token_service = token_service
        self.__auth_unit_of_work = auth_unit_of_work


    async def authenticate_request(self, access_token: str) -> AuthenticatedUserDTO:
        """Autentica a rota com base no token fornecido."""
        try:
            payload = self.__token_service.validate_token(access_token)
            user_id = UserId(payload["sub"])

            async with self.__auth_unit_of_work as uow:
                user = await uow.users_repository.find_by_id(user_id)
                if not user:
                    raise Exception("User not found")

                return AuthenticatedUserDTO(user.id)

        except Exception:
            raise AuthError("Credenciais invalidas")