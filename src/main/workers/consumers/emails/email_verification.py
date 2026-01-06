import asyncio
from src.main.composables.workers.consumers import get_email_verification_consumer_worker




async def run_email_verification_worker():

    email_verification_worker = get_email_verification_consumer_worker()


    await email_verification_worker.start()




if __name__ == "__main__":
    asyncio.run(run_email_verification_worker())
