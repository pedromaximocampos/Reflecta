from abc import ABC, abstractmethod
from typing import Optional
import ssl
import aio_pika
import json
import logging


from aio_pika.abc import AbstractRobustConnection, AbstractChannel, AbstractIncomingMessage, AbstractExchange

from src.domain.exceptions.custom_exceptions.emails_notification_erros import TransientEmailError, PermanentEmailError
from src.infra.messaging.rabbitmq.configs.settings import RabbitMQConsumerConfig

logger = logging.getLogger(__name__)

class BaseRabbitMQConsumerWorker(ABC):

    def __init__(self, consumer_config: RabbitMQConsumerConfig):
        self.__config = consumer_config
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self._dlx_exchange: Optional[AbstractExchange] = None

    async def start(self):
        ssl_default = None
        if self.__config.ssl:
            ssl_default = ssl.create_default_context()
        self._connection = await aio_pika.connect_robust(self.__config.url, ssl_context=ssl_default)

        args = {
            "x-queue-type": "classic",
            "x-dead-letter-exchange": self.__config.dlx_exchange,
            "x-dead-letter-routing-key": self.__config.retry_routing_key,
        }

        async with self._connection:
            logger.info(msg=f"[*] RabbitMQ Consumer Worker started for {self.__config.queue_name}. Waiting for messages...")
            self._channel = await self._connection.channel()

            # Exchange DLX para envio de mensagens para a fila de retry ou para a fila de "mortos"
            self._dlx_exchange = await self._channel.get_exchange(self.__config.dlx_exchange, ensure=True)
            queue = await self._channel.declare_queue(self.__config.queue_name, durable=True, arguments=args)


            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    logger.info(msg=f"[x] Received message: {message.body.decode()}")
                    await self._process_message(message)


    async def _process_message(self, message: AbstractIncomingMessage):
        payload = None

        try:
            payload = json.loads(message.body)

            await self.handle_message(payload)

            await message.ack()

            logger.info(f"[*] Message processed successfully and acknowledged.")

        except TransientEmailError as exc:
            retries = self._get_retry_count(message)

            if retries >= self.__config.max_retries:
                # Caso e mensagem exceda o número maximo de retries, publicamos na DLQ
                await self._publish_to_dlq(payload or {}, message, reason=f"Retries exceeded: {exc}")
                await message.ack()
            else:
                # Ao usarmos o nack com o requeue=False, como nossa configuração da fila possui uma exchange de dead-letter,
                # e uma routing key de retry, a mensagem será roteada para a fila de retry automaticamente.
                await message.nack(requeue=False)

        except PermanentEmailError as exc:
            print(exc)
            await self._publish_to_dlq(payload or {}, message, reason=str(exc))
            await message.ack()

        except Exception as exc:
            print(exc)
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
        logger.info(msg=f"[*] Message with {deaths} deaths numbers.")
        # Normalmente é uma lista de dicts. Usamos o primeiro.
        first = deaths[0] if isinstance(deaths, list) and deaths else {}
        return int(first.get("count", 0))

    async def _publish_to_dlq(self, payload: dict, message: AbstractIncomingMessage, reason: str) -> None:
        assert self._dlx_exchange is not None

        # Preserva headers úteis + adiciona motivo
        headers = dict(message.headers or {})
        headers["x-error-reason"] = reason
        headers["x-original-queue"] = self.__config.queue_name

        logger.info(msg=f"[*] Message published at dlq queue.")

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