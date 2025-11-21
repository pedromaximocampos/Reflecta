from src.domain.exceptions.domain_error import DomainError


class BusinessRuleError(DomainError):
    def __init__(self, message: str = "Business rule violated", **kwargs):
        super().__init__(
            message=message,
            status_code=400,
            name="BusinessRuleError",
            **kwargs,
        )


class OperationNotAllowedError(DomainError):
    def __init__(self, message: str = "Operation not allowed", **kwargs):
        super().__init__(
            message=message,
            status_code=403,
            name="OperationNotAllowedError",
            **kwargs,
        )