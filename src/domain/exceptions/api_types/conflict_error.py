# src/domain/exceptions/api_types/conflict_error.py

from src.domain.exceptions.domain_error import DomainError


class ConflictError(DomainError):
    def __init__(self, message: str = "Conflict", **kwargs):
        super().__init__(
            message=message,
            status_code=409,
            name="ConflictError",
            **kwargs,
        )
