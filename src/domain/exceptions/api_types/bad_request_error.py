# src/domain/exceptions/api_types/bad_request_error.py

from src.domain.exceptions.domain_error import DomainError


class BadRequestError(DomainError):
    def __init__(self, message: str = "Bad request", **kwargs):
        super().__init__(
            message=message,
            status_code=400,
            name="BadRequestError",
            **kwargs,
        )
