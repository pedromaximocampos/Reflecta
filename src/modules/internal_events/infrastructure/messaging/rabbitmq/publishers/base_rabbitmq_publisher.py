import json
from abc import abstractmethod, ABC
from typing import Optional, Tuple

import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractExchange

from src.modules.internal_events.application.ports.messaging.ievent_publisher import IEventPublisher
from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.infrastructure.messaging.rabbitmq.configs.settings import (
    RabbitMQConsumerConfig,
    RabbitMQPublisherConfig,
)
from src.modules.internal_events.infrastructure.messaging.rabbitmq.topology import declare_rabbitmq_topology


class BaseRabbitMQPublisher(IEventPublisher, ABC):


    def __init__(
        self,
        publisher_config: RabbitMQPublisherConfig,
        topology_config: RabbitMQConsumerConfig,
    ) -> None:
        self._config = publisher_config
        self._topology_config = topology_config
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel: Optional[AbstractRobustChannel] = None
        self._exchange: Optional[AbstractExchange] = None


    async def start(self) -> None:
        self._connection = await aio_pika.connect_robust(self._config.url)
        self._channel = await self._connection.channel()
        self._exchange, _, _ = await declare_rabbitmq_topology(
            self._channel,
            self._topology_config,
        )

    async def stop(self) -> None:
        if self._connection:
            await self._connection.close()
        self._connection = None
        self._channel = None
        self._exchange = None


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

    def sync_publish(self, event: OutboxEvent) -> None:
        raise RuntimeError("RabbitMQ publisher supports only asynchronous publishing.")
