from typing import Tuple, Optional
from src.domain.entities.outbox_event import OutboxEvent
from src.infra.messaging.rabbitmq.publishers.base_rabbitmq_publisher import BaseRabbitMQPublisher


class EmailVerificationPublisher(BaseRabbitMQPublisher):


    def _build_message(self, event: OutboxEvent) -> Tuple[dict, Optional[dict]]:
        payload = dict(event.payload)
        payload["verification_url"] = f"{self._config.frontend_base_url}/verify-email?code={event.payload.get("raw_code")}"
        return payload, event.attributes