from src.modules.ai_processing.domain.entities import InboxEvent
from src.modules.ai_processing.domain.value_objects import InboxEventStatus
from src.modules.ai_processing.infrastructure.persistence.postgresql.models import (
    InboxEventModel,
)
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class InboxEventMapper(IMapper[InboxEventModel, InboxEvent]):
    def to_entity(self, model: InboxEventModel) -> InboxEvent:
        return InboxEvent(
            consumer_name=model.consumer_name,
            event_id=model.event_id,
            status=InboxEventStatus(model.status),
            attempts=model.attempts,
            received_at=model.received_at,
            updated_at=model.updated_at,
            lease_expires_at=model.lease_expires_at,
            processed_at=model.processed_at,
            error_code=model.error_code,
            error_message=model.error_message,
        )

    def to_model(self, entity: InboxEvent) -> InboxEventModel:
        return InboxEventModel(
            consumer_name=entity.consumer_name,
            event_id=entity.event_id,
            status=entity.status.value,
            attempts=entity.attempts,
            received_at=entity.received_at,
            updated_at=entity.updated_at,
            lease_expires_at=entity.lease_expires_at,
            processed_at=entity.processed_at,
            error_code=entity.error_code,
            error_message=entity.error_message,
        )
