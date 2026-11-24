from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, ClassVar

from src.modules.internal_events.public import EventType, IDomainEvent, OutboxEvent
from src.modules.sharing.domain.value_objects import ActivityKind


@dataclass(frozen=True, slots=True)
class ProfessionalActivityAssignedItem:
    activity_id: str
    kind: ActivityKind
    title: str
    description: str
    due_date: date | None

    def to_payload(self) -> dict[str, Any]:
        return {
            "activity_id": self.activity_id,
            "activity_kind": self.kind.value,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }


@dataclass(frozen=True, slots=True)
class ProfessionalActivitiesAssigned(IDomainEvent):
    __event_type__: ClassVar[str] = "emails.professional_activities.assigned"

    activities: tuple[ProfessionalActivityAssignedItem, ...]
    user_email: str
    username: str
    occurred_at: datetime

    def to_payload(self) -> dict[str, Any]:
        return {
            "user_email": self.user_email,
            "username": self.username,
            "activities": [item.to_payload() for item in self.activities],
            "occurred_at": self.occurred_at.isoformat(),
        }

    def to_outbox_event(self, event_id: str, created_at: datetime) -> OutboxEvent:
        return OutboxEvent(
            id=event_id,
            event_type=EventType(self.__event_type__),
            payload=self.to_payload(),
            event_occurred_at=self.occurred_at,
            created_at=created_at,
        )
