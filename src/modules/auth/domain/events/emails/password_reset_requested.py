from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any

from src.modules.internal_events.public import OutboxEvent
from src.modules.internal_events.public import IDomainEvent
from src.modules.auth.public.email import Email
from src.modules.internal_events.public import EventType
from src.modules.auth.public.user_id import UserId


@dataclass(frozen=True, slots=True)
class PasswordResetRequested(IDomainEvent):

    __event_type__ = "emails.password_reset.requested"

    user_id: UserId
    username: str
    user_email: Email
    raw_code: str
    expires_in_minutes: int
    occurred_at: datetime

    def to_outbox_event(self, event_id: str, created_at: datetime) -> OutboxEvent:
        message_body = {
            "username": self.username,
            "user_email": self.user_email.value,
            "raw_code": self.raw_code,
            "expires_in": self.expires_in_minutes,
            "occurred_at": self.occurred_at.isoformat(),
        }

        return OutboxEvent(
            id=event_id,
            created_at=created_at,
            event_type=EventType(self.__event_type__),
            event_occurred_at=self.occurred_at,
            payload=message_body
        )

    def to_payload(self) -> dict[str, Any]:
        return super().to_payload()
