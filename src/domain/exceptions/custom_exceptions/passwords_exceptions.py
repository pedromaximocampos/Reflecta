from src.domain.exceptions.domain_error import DomainError



class WeekPasswordException(DomainError):
    """ Exception raised when a password is considered weak according to defined security policies.
    """

    def __init__(self, message: str = "Senha não segue as regras solicitadas", **kwargs):
        super().__init__(
            message=message,
            status_code=422,
            name="WeekPasswordException",
            **kwargs,
        )

class ResetPasswordTokenException(DomainError):
    """ Exception raised when there is an issue with the reset password token.
    """

    def __init__(self, message: str = "Token de redefinição de senha inválido ou expirado", **kwargs):
        super().__init__(
            message=message,
            status_code=400,
            name="ResetPasswordTokenException",
            **kwargs,
        )