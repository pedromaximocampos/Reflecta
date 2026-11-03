from dataclasses import dataclass
from typing import BinaryIO


@dataclass(frozen=True, slots=True)
class ProcessedWorkCoverDTO:
    content: BinaryIO
    content_type: str
    size_bytes: int
    extension: str
