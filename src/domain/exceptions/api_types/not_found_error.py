# src/domain/exceptions/api_types/not_found_error.py

from src.domain.exceptions.domain_error import DomainError


class NotFoundError(DomainError):
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(
            message=message,
            status_code=404,
            name="NotFoundError",
            **kwargs,
        )
