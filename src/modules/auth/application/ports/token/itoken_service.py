from datetime import datetime
from typing import Any, Protocol
from src.modules.auth.public.user_id import UserId
from .dto import GeneratedTokenDTO

class ITokenService(Protocol):
    """Contrato do serviço de tokens."""

    def generate_token(self, user_id: UserId, expires_in_seconds: int, now: datetime) -> GeneratedTokenDTO:
        """Gera um token para o usuário com tempo de expiração."""
        raise NotImplementedError

    def validate_token(self, token: str) -> dict[str, Any]:
        """Valida o token e retorna o ID do usuário associado."""
        raise NotImplementedError