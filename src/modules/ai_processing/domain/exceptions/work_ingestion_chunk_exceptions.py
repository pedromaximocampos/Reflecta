from src.shared.domain.errors.domain_error import DomainError


class InvalidWorkIngestionChunkError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=422,
            name="InvalidWorkIngestionChunkError",
        )


class InvalidWorkIngestionChunkTransitionError(DomainError):
    def __init__(self, current_status: str, target_status: str) -> None:
        super().__init__(
            message=(
                "Work ingestion chunk cannot transition from "
                f"'{current_status}' to '{target_status}'."
            ),
            status_code=409,
            name="InvalidWorkIngestionChunkTransitionError",
        )
