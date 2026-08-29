from datetime import datetime
from typing import Protocol, ClassVar, Any

from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent


class IDomainEvent(Protocol):

    def to_payload(self) -> dict[str, Any]: ...

    def to_outbox_event(self, event_id: str,  occurred_at: datetime) -> OutboxEvent:
        ...