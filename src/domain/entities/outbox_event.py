import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from src.domain.value_objects.event_type import EventType
from src.domain.value_objects.outbox_status import OutboxStatus


@dataclass(eq=False, slots=True)
class OutboxEvent:
    id: str
    event_type: EventType
    payload: dict[str, Any]
    event_occurred_at: datetime
    created_at: datetime
    status: OutboxStatus = OutboxStatus.PENDING
    attempts: int = 0
    sent_at: Optional[datetime] = None
    last_error: Optional[str] = None

    @property
    def attributes(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "event_occurred_at": self.event_occurred_at.isoformat(),
            "created_at": self.created_at.isoformat(),
            "attempts": self.attempts,
            "status": self.status.value,
            "sent_at": self.sent_at.isoformat(),
            "last_error": self.last_error,
        }

    @property
    def payload_json(self) -> str:
        return json.dumps(self.attributes, ensure_ascii=False)
