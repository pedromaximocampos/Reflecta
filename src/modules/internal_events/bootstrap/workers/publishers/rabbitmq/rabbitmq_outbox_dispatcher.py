import asyncio

from src.modules.internal_events.bootstrap.rabbitmq.workers.outbox_dispatcher import (
    get_rabbitmq_outbox_dispatcher_worker,
)


async def run_rabbitmq_publisher_worker() -> None:
    worker = get_rabbitmq_outbox_dispatcher_worker()
    await worker.start()


if __name__ == "__main__":
    asyncio.run(run_rabbitmq_publisher_worker())
