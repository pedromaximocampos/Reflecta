import asyncio

from src.main.composables.messaging.aws.workers.outbox_dispatcher import get_outbox_dispatcher_worker


async def run_sqs_publisher_worker():

    sqs_publisher = get_outbox_dispatcher_worker()

    await sqs_publisher.start()



if __name__ == '__main__':
    asyncio.run(run_sqs_publisher_worker())