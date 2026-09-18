from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.modules.auth.public import AuthenticatedPrincipal, UserRole
from src.modules.auth.application.services.http_request_auth.iauthenticate_request_service import IAuthenticateRequestService

class FastAPIAuthService:


    def __init__(self, authenticate_request_service: IAuthenticateRequestService):
        self._authenticate_request_service = authenticate_request_service

    async def authenticate_request(self, credentials: HTTPAuthorizationCredentials) -> AuthenticatedPrincipal:

        """Autentica a rota com base no token fornecido."""
        try:
            access_token = credentials.credentials

            principal = await self._authenticate_request_service.authenticate_request(access_token)

            return principal

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )



    async def authenticate_user_role(
        self,
        credentials: HTTPAuthorizationCredentials,
        required_role: UserRole,
    ) -> AuthenticatedPrincipal:
        """Autentica a rota com base no token fornecido e verifica se o usuário possui a role necessária."""
        principal = await self.authenticate_request(credentials)

        if principal.role is not required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have the required role",
            )

        return principal
