from abc import ABC, abstractmethod
from typing import Optional

import aio_pika
import json

from aio_pika import Exchange, IncomingMessage
from aio_pika.abc import AbstractRobustConnection, AbstractChannel, AbstractIncomingMessage, AbstractExchange

from src.domain.exceptions.custom_exceptions.emails_notification_erros import TransientEmailError, PermanentEmailError
from src.infra.messaging.rabbitmq.configs.settings import RabbitMQConsumerConfig


class BaseRabbitMQConsumerWorker(ABC):

    def __init__(self, consumer_config: RabbitMQConsumerConfig):
        self.__config = consumer_config
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self._dlx_exchange: Optional[AbstractExchange] = None

    async def start(self):
        self._connection = await aio_pika.connect_robust(self.__config.url)


        async with self._connection:
            self._channel = await self._connection.channel()

            self._dlx_exchange = await self._channel.get_exchange(self.__config.dlx_exchange, ensure=True)
            queue = await self._channel.declare_queue(self.__config.queue_name, durable=True)


            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await self._process_message(message)


    async def _process_message(self, message: AbstractIncomingMessage):
        payload = None

        try:
            payload = json.loads(message.body)

            await self.handle_message(payload)

            await message.ack()

        except TransientEmailError as exc:
            retries = self._get_retry_count(message)

            if retries >= self.__config.max_retries:
                await self._publish_to_dlq(payload or {}, message, reason=f"Retries exceeded: {exc}")
                await message.ack()
            else:
                await message.nack(requeue=False)

        except PermanentEmailError as exc:
            await self._publish_to_dlq(payload or {}, message, reason=str(exc))
            await message.ack()

        except Exception as exc:
            await self._publish_to_dlq(payload or {}, message, reason=f"Unexpected error: {exc}")
            await message.ack()

    @staticmethod
    def _get_retry_count(message: AbstractIncomingMessage) -> int:
        """
        Conta quantas vezes a mensagem já passou por DLX (retry loop),
        usando o header 'x-death' que o RabbitMQ adiciona.
        """
        headers = message.headers or {}
        deaths = headers.get("x-death")
        if not deaths:
            return 0

        # Normalmente é uma lista de dicts. Usamos o primeiro.
        first = deaths[0] if isinstance(deaths, list) and deaths else {}
        return int(first.get("count", 0))

    async def _publish_to_dlq(self, payload: dict, message: AbstractIncomingMessage, reason: str) -> None:
        assert self._dlx_exchange is not None

        # Preserva headers úteis + adiciona motivo
        headers = dict(message.headers or {})
        headers["x-error-reason"] = reason
        headers["x-original-queue"] = self.__config.queue_name

        dlq_msg = aio_pika.Message(
            body=json.dumps(payload).encode(),
            headers=headers,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await self._dlx_exchange.publish(
            dlq_msg,
            routing_key=self.__config.dlx_routing_key,
        )


    @abstractmethod
    async def handle_message(self, payload: dict):
        pass