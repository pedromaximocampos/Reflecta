from datetime import datetime
from typing import Protocol

from src.domain.entities.outbox_event import OutboxEvent


class IOutboxRepository(Protocol):

    async def add_event(self, event: OutboxEvent) -> None: ...

    async def list_pending(self, limit: int) -> list[OutboxEvent]: ...

    async def mark_sent(self, event: OutboxEvent) -> None: ...

    async def mark_failed(self, event: OutboxEvent) -> None: ...