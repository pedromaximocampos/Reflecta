import asyncio

from src.modules.internal_events.bootstrap.aws.workers.outbox_dispatcher import get_outbox_sns_dispatcher_worker


async def sns_worker_publisher() -> None:

    worker = get_outbox_sns_dispatcher_worker()
    await worker.start()


if __name__ == "__main__":
    loop = asyncio.run(sns_worker_publisher())