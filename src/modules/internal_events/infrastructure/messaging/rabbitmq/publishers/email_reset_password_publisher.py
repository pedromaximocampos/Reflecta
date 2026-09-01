from typing import Tuple, Optional

from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.infrastructure.messaging.rabbitmq.publishers.base_rabbitmq_publisher import BaseRabbitMQPublisher


class EmailResetPasswordPublisher(BaseRabbitMQPublisher):
    def _build_message(self, event: OutboxEvent) -> Tuple[dict, Optional[dict]]:
        return dict(event.payload), event.attributes
