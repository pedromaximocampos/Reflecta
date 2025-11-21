# src/domain/exceptions/api_types/database_error.py

from src.domain.exceptions.domain_error import DomainError


class DatabaseError(DomainError):
    def __init__(self, message: str = "Database error", **kwargs):
        super().__init__(
            message=message,
            status_code=500,
            name="DatabaseError",
            **kwargs,
        )
