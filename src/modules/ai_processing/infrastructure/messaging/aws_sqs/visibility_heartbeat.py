import asyncio
import logging

from mypy_boto3_sqs import SQSClient


_LOGGER = logging.getLogger(__name__)


class SQSMessageVisibilityHeartbeat:
    def __init__(
        self,
        *,
        client: SQSClient,
        queue_url: str,
        receipt_handle: str,
        visibility_timeout_seconds: int,
        interval_seconds: int,
    ) -> None:
        self.__client = client
        self.__queue_url = queue_url
        self.__receipt_handle = receipt_handle
        self.__visibility_timeout_seconds = visibility_timeout_seconds
        self.__interval_seconds = interval_seconds
        self.__task: asyncio.Task[None] | None = None
        self.__failure: Exception | None = None

    async def __aenter__(self) -> "SQSMessageVisibilityHeartbeat":
        self.__task = asyncio.create_task(self.__run())
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.__task is None:
            return
        self.__task.cancel()
        try:
            await self.__task
        except asyncio.CancelledError:
            pass
        finally:
            self.__task = None

    def raise_if_failed(self) -> None:
        if self.__failure is not None:
            raise RuntimeError("SQS visibility heartbeat failed.") from self.__failure

    async def __run(self) -> None:
        while True:
            await asyncio.sleep(self.__interval_seconds)
            try:
                await asyncio.to_thread(
                    self.__client.change_message_visibility,
                    QueueUrl=self.__queue_url,
                    ReceiptHandle=self.__receipt_handle,
                    VisibilityTimeout=self.__visibility_timeout_seconds,
                )
            except Exception as error:
                self.__failure = error
                _LOGGER.exception(
                    "SQS visibility heartbeat failed for work ingestion message."
                )
                return
