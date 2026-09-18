from src.shared.domain.errors.domain_error import DomainError


class EmptyThemeBatchError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="At least one theme must be provided.",
            status_code=400,
            name="EmptyThemeBatchError",
        )


class ThemeAlreadyExistsError(DomainError):
    def __init__(self, slug: str | None = None) -> None:
        message = "A theme with the same identifier or slug already exists."
        if slug is not None:
            message = f"A theme with slug '{slug}' already exists."

        super().__init__(
            message=message,
            status_code=409,
            name="ThemeAlreadyExistsError",
        )


class InvalidThemeSlugError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="The theme label must produce a non-empty slug.",
            status_code=400,
            name="InvalidThemeSlugError",
        )


class ThemeNotFoundError(DomainError):
    def __init__(self, theme_id: str) -> None:
        super().__init__(
            message=f"Theme '{theme_id}' was not found.",
            status_code=404,
            name="ThemeNotFoundError",
        )


class EmptyThemeUpdateError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="At least one theme field must be provided for update.",
            status_code=400,
            name="EmptyThemeUpdateError",
        )
