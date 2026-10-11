from dataclasses import dataclass
from datetime import datetime
from typing import Any, ClassVar

from src.modules.auth.public.user_id import UserId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)
from src.modules.internal_events.public import EventType, IDomainEvent, OutboxEvent


@dataclass(frozen=True, slots=True)
class WorkIngestionRequested(IDomainEvent):
    __event_type__: ClassVar[str] = "catalog.work.ingestion.requested"

    ingestion_id: WorkIngestionId
    work_id: WorkId
    requested_by: UserId
    document_location: WorkDocumentLocation
    occurred_at: datetime

    def to_payload(self) -> dict[str, Any]:
        return {
            "ingestion_id": self.ingestion_id.value,
            "work_id": self.work_id.value,
            "requested_by": self.requested_by.value,
            "s3_bucket": self.document_location.bucket,
            "s3_object_key": self.document_location.object_key,
            "occurred_at": self.occurred_at.isoformat(),
        }

    def to_outbox_event(self, event_id: str, created_at: datetime) -> OutboxEvent:
        return OutboxEvent(
            id=event_id,
            created_at=created_at,
            event_type=EventType(self.__event_type__),
            event_occurred_at=self.occurred_at,
            payload=self.to_payload(),
        )
