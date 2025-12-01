import aio_pika
from src.application.ports.messaging.iemail_verification_publisher import IEmailVerificationPublisher
from src.core.settings import get_settings
from src.domain.events.email_verification_requested import EmailVerificationRequested

_settings = get_settings()

class EmailVerificationPublisher(IEmailVerificationPublisher):


    def __init__(self, rabbitmq_url: str, exchange_name: str, routing_key: str):
        self._rabbitmq_url = rabbitmq_url
        self._exchange_name = exchange_name
        self._routing_key = routing_key


    async def publish(self, event: EmailVerificationRequested) -> None:
        connection = await aio_pika.connect_robust(self._rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(self._exchange_name, aio_pika.ExchangeType.FANOUT)

            message_body = {
                "user_name": event.user_name,
                "user_email": str(event.user_email),
                "raw_code": event.raw_code,
                "occurred_at": event.occurred_at.isoformat(),
                "verification_url": f"{_settings.FRONTEND_BASE_URL}/verify-email?code={event.raw_code}"
            }

            message = aio_pika.Message(body=str(message_body).encode())
            await exchange.publish(message, routing_key=self._routing_key)