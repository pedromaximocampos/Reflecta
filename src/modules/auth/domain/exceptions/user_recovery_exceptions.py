from src.shared.domain.errors.domain_error import DomainError


class UserRecoveryTokenError(DomainError):
    def __init__(
        self,
        message: str = "Invalid or expired account recovery code.",
        **kwargs,
    ) -> None:
        super().__init__(
            message=message,
            status_code=400,
            name="UserRecoveryTokenError",
            **kwargs,
        )
