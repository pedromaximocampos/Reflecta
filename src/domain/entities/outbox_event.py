from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from src.domain.value_objects.outbox_status import OutboxStatus


@dataclass(eq=False, slots=True)
class OutboxEvent:
    id: str
    event_type: str
    payload: dict[str, Any]
    event_occurred_at: datetime
    created_at: datetime
    status: OutboxStatus = OutboxStatus.PENDING
    attempts: int = 0
    sent_at: Optional[datetime] = None
    last_error: Optional[str] = None


