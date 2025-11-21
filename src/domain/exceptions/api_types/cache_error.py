# src/domain/exceptions/api_types/cache_error.py

from src.domain.exceptions.domain_error import DomainError


class CacheError(DomainError):
    def __init__(self, message: str = "Cache error", **kwargs):
        super().__init__(
            message=message,
            status_code=500,
            name="CacheError",
            **kwargs,
        )
