from typing import Protocol

from src.domain.entities.outbox_event import OutboxEvent


class IOutboxRepository(Protocol):


    async def add_event(self, event: OutboxEvent) -> None: ...
    # TODO: Implementar métodos para buscar e remover eventos, se necessário