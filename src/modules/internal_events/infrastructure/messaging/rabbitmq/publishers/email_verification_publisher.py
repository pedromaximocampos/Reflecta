from typing import Tuple, Optional
from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.infrastructure.messaging.rabbitmq.publishers.base_rabbitmq_publisher import BaseRabbitMQPublisher


class EmailVerificationPublisher(BaseRabbitMQPublisher):


    def _build_message(self, event: OutboxEvent) -> Tuple[dict, Optional[dict]]:
        payload = dict(event.payload)
        base_url = self._config.frontend_base_url.rstrip("/")
        payload["verification_url"] = f"{base_url}/auth/verify-email?code={event.payload.get('raw_code')}"
        return payload, event.attributes
