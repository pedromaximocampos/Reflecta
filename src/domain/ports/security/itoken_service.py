from abc import ABC, abstractmethod



class ITokenService(ABC):
    """Contrato do serviço de tokens."""

    @abstractmethod
    def generate_token(self, user_id: str, expires_in_seconds: int) -> str:
        """Gera um token para o usuário com tempo de expiração."""
        raise NotImplementedError

    @abstractmethod
    def validate_token(self, token: str) -> str:
        """Valida o token e retorna o ID do usuário associado."""
        raise NotImplementedError