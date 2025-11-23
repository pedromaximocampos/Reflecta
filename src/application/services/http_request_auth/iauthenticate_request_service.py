from abc import abstractmethod, ABC
from dto import AuthenticatedUserDTO

class IAuthenticateRequestService(ABC):

    """Contrato do serviço de autenticação de rotas."""

    @abstractmethod
    async def authenticate_request(self, access_token: str) -> AuthenticatedUserDTO:
        """Autentica a rota com base no token fornecido."""
        raise NotImplementedError