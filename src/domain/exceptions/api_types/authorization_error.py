# src/domain/exceptions/api_types/authorization_error.py

from src.domain.exceptions.domain_error import DomainError


class AuthError(DomainError):
    def __init__(self, message: str = "Unauthorized", **kwargs):
        super().__init__(
            message=message,
            status_code=401,
            name="AuthError",
            **kwargs,
        )
