from src.shared.domain.errors.domain_error import DomainError


class TransientEmailError(DomainError):
    pass

class PermanentEmailError(DomainError):
    pass