from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.domain.value_objects.event_type import EventType
from src.infra.postgresql.mappers.interface.imapper import IMapper
from src.modules.internal_events.infrastructure.persistence.postgresql.models.outbox_model import OutboxModel


class OutboxMapper(IMapper[OutboxModel, OutboxEvent]):

    def to_entity(self, model: OutboxModel) -> OutboxEvent:
        return OutboxEvent(
            id=model.id,
            event_type=EventType(model.event_type),
            payload=model.payload,
            event_occurred_at=model.event_occurred_at,
            created_at=model.created_at,
            status=model.status,
            attempts=model.attempts,
            sent_at=model.sent_at,
            last_error=model.last_error,
        )


    def to_model(self, entity: OutboxEvent) -> OutboxModel:
        return OutboxModel(
            id=entity.id,
            event_type=entity.event_type.value,
            payload=entity.payload,
            event_occurred_at=entity.event_occurred_at,
            created_at=entity.created_at,
            status=entity.status,
            attempts=entity.attempts,
            sent_at=entity.sent_at,
            last_error=entity.last_error,
        )