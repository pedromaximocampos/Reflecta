from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.value_objects.user_id import UserId
from .dto import GeneratedTokenDTO

class ITokenService(ABC):
    """Contrato do serviço de tokens."""

    @abstractmethod
    def generate_token(self, user_id: UserId, expires_in_seconds: int, now: datetime) -> GeneratedTokenDTO:
        """Gera um token para o usuário com tempo de expiração."""
        raise NotImplementedError

    @abstractmethod
    def validate_token(self, token: str) -> str:
        """Valida o token e retorna o ID do usuário associado."""
        raise NotImplementedError