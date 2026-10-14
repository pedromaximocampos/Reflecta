from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StorageObjectLocationDTO:
    bucket: str
    object_key: str

    def __post_init__(self) -> None:
        if not self.bucket.strip():
            raise ValueError("Storage bucket must not be empty.")
        if not self.object_key.strip():
            raise ValueError("Storage object key must not be empty.")


@dataclass(frozen=True, slots=True)
class StoredNormalizedTextDTO:
    location: StorageObjectLocationDTO
    content_sha256: str
    size_bytes: int
    etag: str | None = None
    version_id: str | None = None

    def __post_init__(self) -> None:
        if len(self.content_sha256) != 64:
            raise ValueError("Normalized text SHA-256 must contain 64 characters.")
        if self.size_bytes <= 0:
            raise ValueError("Normalized text must not be empty.")
