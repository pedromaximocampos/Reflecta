from src.shared.domain.errors.domain_error import DomainError


class PassageNotFoundError(DomainError):
    def __init__(self, passage_id: str) -> None:
        super().__init__(
            message=f"Passage '{passage_id}' was not found.",
            status_code=404,
            name="PassageNotFoundError",
        )


class EmptyPassageUpdateError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="At least one passage field must be provided.",
            status_code=400,
            name="EmptyPassageUpdateError",
        )


class InvalidPassageTransitionError(DomainError):
    def __init__(self, current_status: str, target_status: str) -> None:
        super().__init__(
            message=(
                f"Passage cannot transition from '{current_status}' "
                f"to '{target_status}'."
            ),
            status_code=409,
            name="InvalidPassageTransitionError",
        )


class InactivePassageThemeError(DomainError):
    def __init__(self, theme_id: str) -> None:
        super().__init__(
            message=f"Theme '{theme_id}' is not active for passage association.",
            status_code=409,
            name="InactivePassageThemeError",
        )


class InvalidPassageThemesError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="Passage themes must be non-empty and unique.",
            status_code=400,
            name="InvalidPassageThemesError",
        )
