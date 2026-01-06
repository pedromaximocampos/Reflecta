from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from src.domain.entities.outbox_event import OutboxEvent
from src.domain.events.idomain_event import IDomainEvent
from src.domain.value_objects.email import Email
from src.domain.value_objects.user_id import UserId


@dataclass(frozen=True, slots=True)
class EmailVerificationRequested(IDomainEvent):

    __event_type__ = "emails.verification.requested"

    user_id: UserId
    username: str
    user_email: Email
    raw_code: str
    occurred_at: datetime

    def to_outbox_event(self, event_id: str, created_at: datetime) -> OutboxEvent:
        message_body = {
            "username": self.username,
            "user_email": self.user_email.value,
            "raw_code": self.raw_code,
            "occurred_at": self.occurred_at.isoformat(),
        }

        return OutboxEvent(
            id=event_id,
            created_at=created_at,
            event_type=self.__event_type__,
            event_occurred_at=self.occurred_at,
            payload=message_body
        )

    def to_payload(self) -> dict[str, Any]:
        return super().to_payload()