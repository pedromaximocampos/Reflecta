from src.modules.notification.application.ports.handlers.iemail_event_handler import IEmailEventHandler
from src.modules.notification.domain.value_objects.event_types import EventType
from src.modules.notification.infrastructure.messaging.rabbitmq.consumers.base_rabbitmq_consumer_worker import BaseRabbitMQConsumerWorker
from src.modules.internal_events.infrastructure.messaging.rabbitmq.configs.settings import RabbitMQConsumerConfig


class EmailVerificationConsumerWorker(BaseRabbitMQConsumerWorker):
    EVENT_TYPE = EventType.EMAIL_VERIFICATION_REQUESTED

    def __init__(
        self,
        consumer_config: RabbitMQConsumerConfig,
        email_event_handler: IEmailEventHandler,
    ) -> None:
        super().__init__(consumer_config)
        self.__email_event_handler = email_event_handler

    async def handle_message(self, payload: dict) -> None:
        await self.__email_event_handler.handle(
            event_type=self.EVENT_TYPE,
            payload=payload,
        )

