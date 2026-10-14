from dataclasses import dataclass
from typing import BinaryIO

from src.modules.auth.public import UserId
from src.modules.catalog.domain.entities.work_ingestion import WorkIngestion
from src.modules.catalog.domain.value_objects.work_ingestion_status import (
    WorkIngestionStatus,
)
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(frozen=True, slots=True)
class RequestWorkIngestionInputDTO:
    work_id: WorkId
    requested_by: UserId
    filename: str
    content_type: str
    size_bytes: int
    content: BinaryIO


@dataclass(frozen=True, slots=True)
class RequestWorkIngestionOutputDTO:
    ingestion_id: WorkIngestionId
    work_id: WorkId
    status: WorkIngestionStatus

    @classmethod
    def from_entity(
        cls,
        ingestion: WorkIngestion,
    ) -> "RequestWorkIngestionOutputDTO":
        return cls(
            ingestion_id=ingestion.id,
            work_id=ingestion.work_id,
            status=ingestion.status,
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "ingestion_id": self.ingestion_id.value,
            "work_id": self.work_id.value,
            "status": self.status.value,
        }
