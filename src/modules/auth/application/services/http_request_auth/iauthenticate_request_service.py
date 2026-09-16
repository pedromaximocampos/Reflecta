from typing import Protocol
from src.modules.auth.public import AuthenticatedPrincipal

class IAuthenticateRequestService(Protocol):

    """Contrato do serviço de autenticação de rotas."""

    async def authenticate_request(self, access_token: str) -> AuthenticatedPrincipal:
        """Autentica a rota com base no token fornecido."""
        raise NotImplementedError
