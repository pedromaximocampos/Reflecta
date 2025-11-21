# src/domain/exceptions/api_types/user_is_not_admin.py

from src.domain.exceptions.domain_error import DomainError


class UserIsNotAdmin(DomainError):
    def __init__(self, message: str = "User is not admin", **kwargs):
        super().__init__(
            message=message,
            status_code=403,
            name="UserIsNotAdmin",
            **kwargs,
        )
