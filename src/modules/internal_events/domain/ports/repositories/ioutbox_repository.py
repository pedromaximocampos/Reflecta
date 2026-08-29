from datetime import datetime
from typing import Protocol

from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent


class IOutboxRepository(Protocol):

    async def add_event(self, event: OutboxEvent) -> None: ...

    async def claim_pending(self, batch_limit: int, attempts_limit: int) -> list[OutboxEvent]: ...

    async def mark_sent(self, event: OutboxEvent) -> None: ...

    async def mark_failed(self, event: OutboxEvent) -> None: ...