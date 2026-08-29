from typing import Protocol
from src.modules.auth.application.services.http_request_auth.dto import AuthenticatedUserDTO

class IAuthenticateRequestService(Protocol):

    """Contrato do serviço de autenticação de rotas."""

    async def authenticate_request(self, access_token: str) -> AuthenticatedUserDTO:
        """Autentica a rota com base no token fornecido."""
        raise NotImplementedError
