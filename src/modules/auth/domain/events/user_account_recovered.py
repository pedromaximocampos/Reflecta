from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.modules.auth.public.user_id import UserId
from src.modules.internal_events.public import EventType, IDomainEvent, OutboxEvent


@dataclass(frozen=True, slots=True)
class UserAccountRecovered(IDomainEvent):
    __event_type__ = "auth.user.recovered"

    user_id: UserId
    occurred_at: datetime

    def to_payload(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id.value,
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
