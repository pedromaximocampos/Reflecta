from src.shared.domain.errors.domain_error import DomainError


class EmptyJournalContentError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="Journal content cannot be empty.",
            status_code=400,
            name="EmptyJournalContentError",
        )


class EmptyJournalUpdateError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="At least one journal field must be provided for update.",
            status_code=400,
            name="EmptyJournalUpdateError",
        )


class JournalEntryNotEditableError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="Only draft journal entries can be edited.",
            status_code=409,
            name="JournalEntryNotEditableError",
        )


class JournalEntryNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="Journal entry was not found.",
            status_code=404,
            name="JournalEntryNotFoundError",
        )
