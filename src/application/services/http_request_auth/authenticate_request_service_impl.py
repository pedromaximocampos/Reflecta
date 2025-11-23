from iauthenticate_request_service import IAuthenticateRequestService
from src.application.services.http_request_auth.dto import AuthenticatedUserDTO
from src.application.services.token.itoken_service import ITokenService
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.exceptions.api_types import AuthError

class AuthenticateRequestServiceImpl(IAuthenticateRequestService):

    def __init__(self, user_repository: IUserRepository, token_service: ITokenService):
        self._user_repository = user_repository
        self._token_service = token_service


    async def authenticate_request(self, access_token: str) -> AuthenticatedUserDTO:
        """Autentica a rota com base no token fornecido."""
        try:
            payload = self._token_service.validate_token(access_token)
            user_id = payload["sub"]


            user = await self._user_repository.find_by_id(user_id)
            if not user:
                raise Exception("User not found")

            return AuthenticatedUserDTO(user.id)


        except Exception:
            raise AuthError("Credenciais invalidas")