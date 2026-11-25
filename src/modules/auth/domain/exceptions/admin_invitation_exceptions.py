from src.shared.domain.errors.domain_error import DomainError


class AdminInvitationTargetNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="No active account was found for this email.",
            status_code=404,
        )


class AdminInvitationEmailNotVerifiedError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="The invited account must verify its email first.",
            status_code=409,
        )


class AdminInvitationAlreadyAdminError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="This account is already an administrator.",
            status_code=409,
        )


class AdminInvitationTokenError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="The administrator invitation is invalid, expired, or already used.",
            status_code=400,
        )


class AdminInvitationNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="Administrator invitation not found.",
            status_code=404,
        )


class AdminInvitationStateError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="This administrator invitation can no longer be changed.",
            status_code=409,
        )


class AdminInvitationForbiddenError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="Only an administrator can manage administrator invitations.",
            status_code=403,
        )
