from typing import Protocol

from src.domain.events.idomain_event import IDomainEvent
from src.domain.ports.repositories.ioutbox_repository import IOutboxRepository


class IOutboxService(Protocol):

    async def persist_event(self, event: IDomainEvent, outbox_repo: IOutboxRepository) -> None:
        ...