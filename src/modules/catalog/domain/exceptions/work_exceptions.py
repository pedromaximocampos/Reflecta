from src.shared.domain.errors.domain_error import DomainError


class WorkAlreadyExistsError(DomainError):
    def __init__(self, slug: str | None = None) -> None:
        message = "A work with the same identifier or slug already exists."
        if slug is not None:
            message = f"A work with slug '{slug}' already exists."
        super().__init__(message=message, status_code=409, name="WorkAlreadyExistsError")


class InvalidWorkSlugError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="The work title must produce a non-empty slug.",
            status_code=400,
            name="InvalidWorkSlugError",
        )


class InvalidAuthorNameError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="The author name must produce a non-empty normalized name.",
            status_code=400,
            name="InvalidAuthorNameError",
        )


class WorkNotFoundError(DomainError):
    def __init__(self, work_id: str) -> None:
        super().__init__(
            message=f"Work '{work_id}' was not found.",
            status_code=404,
            name="WorkNotFoundError",
        )


class InvalidWorkDocumentError(DomainError):
    def __init__(self, message: str = "The uploaded work document is invalid.") -> None:
        super().__init__(
            message=message,
            status_code=422,
            name="InvalidWorkDocumentError",
        )


class InvalidWorkIngestionTransitionError(DomainError):
    def __init__(self, current_status: str, target_status: str) -> None:
        super().__init__(
            message=(
                "Work ingestion cannot transition from "
                f"'{current_status}' to '{target_status}'."
            ),
            status_code=409,
            name="InvalidWorkIngestionTransitionError",
        )
