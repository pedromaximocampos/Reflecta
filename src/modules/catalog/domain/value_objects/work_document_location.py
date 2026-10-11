from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WorkDocumentLocation:
    bucket: str
    object_key: str

    def __post_init__(self) -> None:
        if not self.bucket.strip():
            raise ValueError("Work document bucket must not be empty.")
        if not self.object_key.strip():
            raise ValueError("Work document object key must not be empty.")
