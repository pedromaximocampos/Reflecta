from typing import Protocol

from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent


class IEventPublisher(Protocol):

    async def start(self) -> None: ...

    async def publish(self, event: OutboxEvent) -> None: ...

    def sync_publish(self, event: OutboxEvent) -> None: ...

    async def stop(self) -> None: ...
