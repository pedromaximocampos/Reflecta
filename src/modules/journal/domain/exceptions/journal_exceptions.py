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
            message="A journal entry being analyzed cannot be edited.",
            status_code=409,
            name="JournalEntryNotEditableError",
        )


class FutureJournalEntryDateError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="Journal entry date cannot be in the future.",
            status_code=400,
            name="FutureJournalEntryDateError",
        )


class JournalEntryDateConflictError(DomainError):
    def __init__(self, *, entry_id: str, entry_date: str) -> None:
        super().__init__(
            message="A journal entry already exists for this date.",
            status_code=409,
            name="JournalEntryDateConflictError",
            details={
                "existing_entry_id": entry_id,
                "entry_date": entry_date,
            },
        )


class InvalidJournalCalendarRangeError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="The journal calendar range must contain between 1 and 366 days.",
            status_code=400,
            name="InvalidJournalCalendarRangeError",
        )


class InvalidJournalWindowError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="The journal window parameters are invalid.",
            status_code=400,
            name="InvalidJournalWindowError",
        )


class JournalEntryNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            message="Journal entry was not found.",
            status_code=404,
            name="JournalEntryNotFoundError",
        )
