# src/domain/exceptions/api_types/forbidden_error.py

from src.domain.exceptions.domain_error import DomainError


class ForbiddenError(DomainError):
    def __init__(self, message: str = "Forbidden", **kwargs):
        super().__init__(
            message=message,
            status_code=403,
            name="ForbiddenError",
            **kwargs,
        )
