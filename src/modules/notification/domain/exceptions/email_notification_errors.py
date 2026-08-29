from src.domain.exceptions.domain_error import DomainError


class TransientEmailError(DomainError):
    pass

class PermanentEmailError(DomainError):
    pass