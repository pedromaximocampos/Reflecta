from src.domain.exceptions.domain_error import DomainError


class EmailVerificationTokenAlreadyExistsError(DomainError):
    def __init__(self, message: str = "Um token de verificação já está ativo para este usuário.", **kwargs):
        super().__init__(
            message=message,
            status_code=409,   # conflito: operação não pode ser realizada neste estado
            name="EmailVerificationTokenAlreadyExistsError",
            **kwargs,
        )


class EmailAlreadyExistsError(DomainError):
    def __init__(self, message: str = "This email is already associated to a user", **kwargs):
        super().__init__(
            message=message,
            status_code=409,  # conflito — recurso já existe
            name="EmailAlreadyExistsError",
            **kwargs,
        )

class UsernameAlreadyExistsError(DomainError):
    def __init__(self, message: str = "Este nome de usuário já está em uso.", **kwargs):
        super().__init__(
            message=message,
            status_code=409,
            name="UsernameAlreadyExistsError",
            **kwargs,
        )


class UserNotFoundError(DomainError):
    def __init__(self, message: str = "User not found.", **kwargs):
        super().__init__(
            message=message,
            status_code=404,  # não encontrado
            name="UserNotFoundError",
            **kwargs,
        )