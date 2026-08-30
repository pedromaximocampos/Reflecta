from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.domain.events.idomain_event import IDomainEvent
from src.modules.internal_events.domain.ports.repositories.ioutbox_repository import IOutboxRepository
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator
from .ioutbox_service import IOutboxService




class OutboxServiceImpl(IOutboxService):


    def __init__(self, system_clock:IClock, ulid_generator: IULIDGenerator) -> None:
        self.__clock = system_clock
        self.__ulid_generator = ulid_generator

    async def persist_event(self, event: IDomainEvent, outbox_repo: IOutboxRepository) -> None:

        outbox_event = self.__return_outbox_event_entity(event)
        await outbox_repo.add_event(outbox_event)



    def __return_outbox_event_entity(self, event: IDomainEvent) -> OutboxEvent:
        event_id = self.__ulid_generator.generate_ulid()
        now = self.__clock.now()
        return event.to_outbox_event(event_id, now)
