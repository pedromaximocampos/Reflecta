from dataclasses import dataclass
from typing import BinaryIO

from src.modules.catalog.public.work_id import WorkId


@dataclass(frozen=True, slots=True)
class ReplaceWorkCoverInputDTO:
    work_id: WorkId
    content: BinaryIO
    content_type: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class RemoveWorkCoverInputDTO:
    work_id: WorkId
