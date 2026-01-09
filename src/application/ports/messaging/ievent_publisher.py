from typing import Protocol

from src.domain.entities.outbox_event import OutboxEvent


class IEventPublisherWorker(Protocol):

    async def publish(self, event: OutboxEvent) -> None: ...

    def sync_publish(self, event: OutboxEvent) -> None: ...