from typing import Any, Dict, Optional


class DomainError(Exception):
    """
    Base para todas as exceções de domínio / API.

    Atributos:
        message: mensagem principal do erro (voltada ao cliente ou logs).
        status_code: HTTP status associado (400, 401, 404, 500...).
        name: nome lógico da exceção (usado no payload de erro).
        details: payload opcional com detalhes extras (ex: errors do Pydantic).
        extra: dicionário com quaisquer outros kwargs fornecidos.
    """

    def __init__(
        self,
        message: str = "",
        status_code: int = 400,
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message)
        self.message: str = message
        self.status_code: int = status_code
        self.name: str = name or self.__class__.__name__
        self.details: Any = kwargs.get("details")
        # qualquer outra chave passada em kwargs fica disponível em .extra
        self.extra: Dict[str, Any] = kwargs
