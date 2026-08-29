from typing import Tuple, Optional

from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.infrastructure.messaging.rabbitmq.publishers.base_rabbitmq_publisher import BaseRabbitMQPublisher


class EmailResetPasswordPublisher(BaseRabbitMQPublisher):


    def _build_message(self, event: OutboxEvent) -> Tuple[dict, Optional[dict]]:
        payload = dict(event.payload)
        payload["reset_password_link"] =  f"{self._config.frontend_base_url}/reset-password?code={event.payload.get("raw_code")}"
        return payload, event.attributes