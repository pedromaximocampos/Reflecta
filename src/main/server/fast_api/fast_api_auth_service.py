from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.application.services.http_request_auth.iauthenticate_request_service import IAuthenticateRequestService
from src.application.services.http_request_auth.dto import AuthenticatedUserDTO

class FastAPIAuthService:


    def __init__(self, authenticate_request_service: IAuthenticateRequestService):
        self._security = HTTPBearer()
        self._authenticate_request_service = authenticate_request_service

    async def authenticate_request(self, credentials: HTTPAuthorizationCredentials) -> AuthenticatedUserDTO:

        """Autentica a rota com base no token fornecido."""
        try:
            access_token = credentials.credentials

            user: AuthenticatedUserDTO = await self._authenticate_request_service.authenticate_request(access_token)

            return user

        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )