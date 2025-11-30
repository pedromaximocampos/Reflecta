from src.domain.exceptions.domain_error import DomainError


class EmailVerificationException(DomainError):
    def __init__(self, message: str = "Codigo invalido ou usuario ja verificado", **kwargs):
        super().__init__(
            message=message,
            status_code=409,  # conflito: operação não pode ser realizada neste estado
            name="EmailVerificationException",
            **kwargs,
        )