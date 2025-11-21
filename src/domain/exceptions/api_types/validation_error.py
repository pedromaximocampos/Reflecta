# src/domain/exceptions/api_types/validation_error.py

from src.domain.exceptions.domain_error import DomainError


class ValidationFailed(DomainError):
    def __init__(self, message: str = "Invalid request data", **kwargs):
        super().__init__(
            message=message,
            status_code=400,  # se quiser, pode ser 422
            name="ValidationFailed",
            **kwargs,
        )
