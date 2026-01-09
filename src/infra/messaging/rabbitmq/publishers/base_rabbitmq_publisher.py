import json
from abc import abstractmethod, ABC
from typing import Optional, Tuple

import aio_pika
from aio_pika import Exchange, Channel
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractExchange

from src.application.ports.messaging.ievent_publisher import IEventPublisherWorker
from src.domain.entities.outbox_event import OutboxEvent
from src.infra.messaging.rabbitmq.configs.settings import RabbitMQPublisherConfig


class BaseRabbitMQPublisherWorker(IEventPublisherWorker, ABC):


    def __init__(self, publisher_config: RabbitMQPublisherConfig) -> None:
        self._config = publisher_config
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel: Optional[AbstractRobustChannel] = None
        self._exchange: Optional[AbstractExchange] = None


    async def start(self) -> None:
        self._connection = await aio_pika.connect_robust(self._config.url)
        self._channel = await self._connection.channel()
        self._exchange = await self._channel.get_exchange(
                self._config.exchange_name,
                ensure=True,
            )

    async def stop(self) -> None:
        if self._connection:
            await self._connection.close()


    @abstractmethod
    def _build_message(self, event: OutboxEvent) -> Tuple[dict, Optional[dict]]: ...

    async def publish(self, event: OutboxEvent) -> None:
        if not self._exchange:
            raise RuntimeError("Publisher not started. Call start() first.")

        payload, attributes = self._build_message(event)

        message = aio_pika.Message(body=json.dumps(payload).encode(),
                                       content_type="application/json",
                                       delivery_mode=aio_pika.DeliveryMode.PERSISTENT,)

        await self._exchange.publish(message, routing_key=self._config.routing_key)