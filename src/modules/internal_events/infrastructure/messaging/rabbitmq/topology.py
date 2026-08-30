from aio_pika import ExchangeType
from aio_pika.abc import AbstractExchange, AbstractQueue, AbstractRobustChannel

from src.modules.internal_events.infrastructure.messaging.rabbitmq.configs.settings import RabbitMQConsumerConfig


async def declare_rabbitmq_topology(
    channel: AbstractRobustChannel,
    config: RabbitMQConsumerConfig,
) -> tuple[AbstractExchange, AbstractExchange, AbstractQueue]:
    main_exchange = await channel.declare_exchange(
        config.exchange_name,
        ExchangeType.DIRECT,
        durable=True,
    )
    dead_letter_exchange = await channel.declare_exchange(
        config.dlx_exchange,
        ExchangeType.DIRECT,
        durable=True,
    )

    main_queue = await channel.declare_queue(
        config.queue_name,
        durable=True,
        arguments={
            "x-queue-type": "classic",
            "x-dead-letter-exchange": config.dlx_exchange,
            "x-dead-letter-routing-key": config.retry_routing_key,
        },
    )
    retry_queue = await channel.declare_queue(
        config.retry_queue_name,
        durable=True,
        arguments={
            "x-message-ttl": 5_000,
            "x-dead-letter-exchange": config.exchange_name,
            "x-dead-letter-routing-key": config.routing_key,
        },
    )
    dead_letter_queue = await channel.declare_queue(
        config.dlx_queue_name,
        durable=True,
    )

    await main_queue.bind(main_exchange, routing_key=config.routing_key)
    await retry_queue.bind(dead_letter_exchange, routing_key=config.retry_routing_key)
    await dead_letter_queue.bind(dead_letter_exchange, routing_key=config.dlx_routing_key)

    return main_exchange, dead_letter_exchange, main_queue
