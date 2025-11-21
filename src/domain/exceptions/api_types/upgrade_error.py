# src/domain/exceptions/api_types/upgrade_error.py

from src.domain.exceptions.domain_error import DomainError


class UpgradeRequired(DomainError):
    def __init__(self, message: str = "Upgrade required", **kwargs):
        super().__init__(
            message=message,
            status_code=426,  # HTTP 426 Upgrade Required
            name="UpgradeRequired",
            **kwargs,
        )
