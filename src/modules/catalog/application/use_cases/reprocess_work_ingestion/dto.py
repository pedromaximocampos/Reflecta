from dataclasses import dataclass

from src.modules.catalog.domain.entities.work_ingestion import WorkIngestion
from src.modules.catalog.domain.value_objects import WorkIngestionStatus
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(frozen=True, slots=True)
class ReprocessWorkIngestionInputDTO:
    ingestion_id: WorkIngestionId


@dataclass(frozen=True, slots=True)
class ReprocessWorkIngestionOutputDTO:
    ingestion_id: WorkIngestionId
    work_id: WorkId
    status: WorkIngestionStatus
    event_created: bool

    @classmethod
    def from_entity(
        cls,
        ingestion: WorkIngestion,
        *,
        event_created: bool,
    ) -> "ReprocessWorkIngestionOutputDTO":
        return cls(
            ingestion_id=ingestion.id,
            work_id=ingestion.work_id,
            status=ingestion.status,
            event_created=event_created,
        )

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "ingestion_id": self.ingestion_id.value,
            "work_id": self.work_id.value,
            "status": self.status.value,
            "event_created": self.event_created,
        }
