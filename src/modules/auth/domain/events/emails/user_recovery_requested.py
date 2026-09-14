from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.modules.auth.public.email import Email
from src.modules.auth.public.user_id import UserId
from src.modules.internal_events.public import EventType, IDomainEvent, OutboxEvent


@dataclass(frozen=True, slots=True)
class UserRecoveryRequested(IDomainEvent):
    __event_type__ = "emails.recovery_user.requested"

    user_id: UserId
    username: str
    user_email: Email
    raw_code: str
    expires_in_minutes: int
    occurred_at: datetime

    def to_payload(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "user_email": self.user_email.value,
            "raw_code": self.raw_code,
            "expires_in": self.expires_in_minutes,
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
