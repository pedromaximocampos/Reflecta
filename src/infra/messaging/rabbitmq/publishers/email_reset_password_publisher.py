import json

import aio_pika

from src.application.ports.messaging.ipassword_reset_publisher import IPasswordResetPublisher
from src.domain.events.password_reset_requested import PasswordResetRequested
from src.infra.messaging.rabbitmq.configs.settings import RabbitMQPublisherConfig


class EmailResetPasswordPublisher(IPasswordResetPublisher):


    def __init__(self, publisher_config: RabbitMQPublisherConfig) -> None:
        self.__config = publisher_config

    async def publish_password_reset_requested(self, password_reset_event: PasswordResetRequested) -> None:
        connection = await aio_pika.connect_robust(self.__config.url)
        async with connection:
            channel = await connection.channel()
            exchange  = await channel.get_exchange(self.__config.exchange_name, ensure=True)

            message_body = {
                "username": password_reset_event.username,
                "user_email": str(password_reset_event.user_email),
                "raw_code": password_reset_event.raw_code,
                "occurred_at": password_reset_event.occurred_at.isoformat(),
                "reset_password_link": f"{self.__config.frontend_base_url}/reset-password?code={password_reset_event.raw_code}"
            }

            message = aio_pika.Message( body=json.dumps(message_body).encode(),
                                        content_type="application/json",
                                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,)
            await exchange.publish(message, routing_key=self.__config.routing_key)