from src.shared.domain.errors.domain_error import DomainError


class EmailVerificationException(DomainError):
    def __init__(self, message: str = "You are not yet verified. A verification code has been sent to your email.", **kwargs):
        super().__init__(
            message=message,
            status_code=409,  # conflito: operação não pode ser realizada neste estado
            name="EmailVerificationException",
            **kwargs,
        )