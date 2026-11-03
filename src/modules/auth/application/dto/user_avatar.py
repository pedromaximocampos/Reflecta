from dataclasses import dataclass
from typing import BinaryIO


@dataclass(frozen=True, slots=True)
class ProcessedUserAvatarDTO:
    content: BinaryIO
    content_type: str
    size_bytes: int
    extension: str


@dataclass(frozen=True, slots=True)
class StoredUserAvatarDTO:
    object_key: str
    content_type: str
    size_bytes: int
    etag: str | None = None
    version_id: str | None = None
