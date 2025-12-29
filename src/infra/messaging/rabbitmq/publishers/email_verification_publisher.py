import aio_pika
from src.application.ports.messaging.iemail_verification_publisher import IEmailVerificationPublisher
from src.domain.events.email_verification_requested import EmailVerificationRequested
from src.infra.messaging.rabbitmq.configs.settings import RabbitMQPublisherConfig


class EmailVerificationPublisher(IEmailVerificationPublisher):


    def __init__(self, publisher_config: RabbitMQPublisherConfig) -> None:
        self.__config = publisher_config

    async def publish(self, event: EmailVerificationRequested) -> None:
        connection = await aio_pika.connect_robust(self.__config.url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(self.__config.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True)

            message_body = {
                "username": event.username,
                "user_email": str(event.user_email),
                "raw_code": event.raw_code,
                "occurred_at": event.occurred_at.isoformat(),
                "verification_url": f"{self.__config.frontend_base_url}/verify-email?code={event.raw_code}"
            }

            message = aio_pika.Message(body=str(message_body).encode())
            await exchange.publish(message, routing_key=self.__config.routing_key)