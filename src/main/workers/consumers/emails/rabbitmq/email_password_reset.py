import asyncio
from src.main.composables.messaging.rabbitmq.workers.consumers import get_password_reset_consumer_worker




async def run_email_password_reset_worker():

    password_reset_worker = get_password_reset_consumer_worker()

    await password_reset_worker.start()


if __name__ == "__main__":
    asyncio.run(run_email_password_reset_worker())
