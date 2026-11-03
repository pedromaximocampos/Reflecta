from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StoredWorkCoverDTO:
    object_key: str
    content_type: str
    size_bytes: int
    etag: str | None = None
    version_id: str | None = None
