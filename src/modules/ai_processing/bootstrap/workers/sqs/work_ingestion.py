import asyncio

from src.modules.ai_processing.bootstrap.consumers import (
    build_work_ingestion_consumer,
)
from src.modules.ai_processing.bootstrap.use_cases import (
    get_process_work_ingestion_use_case,
)


async def run_work_ingestion_worker() -> None:
    worker = build_work_ingestion_consumer(get_process_work_ingestion_use_case())
    await worker.start()


if __name__ == "__main__":
    asyncio.run(run_work_ingestion_worker())
