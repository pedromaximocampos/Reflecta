import asyncio
import logging
from typing import Any

from mypy_boto3_sqs import SQSClient

from src.modules.ai_processing.application.ports.inbox import IWorkIngestionInbox
from src.modules.ai_processing.application.use_cases.process_work_ingestion import (
    IProcessWorkIngestionUseCase,
)
from src.modules.ai_processing.domain.value_objects import InboxClaimOutcome
from src.modules.ai_processing.infrastructure.messaging.aws_sqs.inbox_heartbeat import (
    InboxClaimHeartbeat,
)
from src.modules.ai_processing.infrastructure.messaging.aws_sqs.configs import (
    WorkIngestionSQSSettings,
)
from src.modules.ai_processing.infrastructure.messaging.aws_sqs.message_parser import (
    WorkIngestionRequestedMessageParser,
)
from src.modules.ai_processing.infrastructure.messaging.aws_sqs.visibility_heartbeat import (
    SQSMessageVisibilityHeartbeat,
)
from src.modules.internal_events.application.ports.messaging.ievent_consumer_worker import (
    IEventConsumerWorker,
)


_LOGGER = logging.getLogger(__name__)


class SQSWorkIngestionConsumerWorker(IEventConsumerWorker):
    def __init__(
        self,
        *,
        client: SQSClient,
        settings: WorkIngestionSQSSettings,
        use_case: IProcessWorkIngestionUseCase,
        inbox: IWorkIngestionInbox,
        parser: WorkIngestionRequestedMessageParser | None = None,
    ) -> None:
        self.__client = client
        self.__settings = settings
        self.__use_case = use_case
        self.__inbox = inbox
        self.__parser = parser or WorkIngestionRequestedMessageParser()
        self.__stopped = False

    async def start(self) -> None:
        self.__stopped = False
        _LOGGER.info("Work ingestion SQS consumer started.")
        while not self.__stopped:
            await self.run_once()

    async def stop(self) -> None:
        self.__stopped = True

    async def handle_message(self, payload: dict) -> None:
        await self.__process_message(payload)

    async def run_once(self) -> int:
        response = await asyncio.to_thread(
            self.__client.receive_message,
            QueueUrl=self.__settings.queue_url,
            MaxNumberOfMessages=self.__settings.max_number_of_messages,
            WaitTimeSeconds=self.__settings.wait_time_seconds,
            VisibilityTimeout=self.__settings.visibility_timeout_seconds,
            MessageAttributeNames=["All"],
            AttributeNames=["ApproximateReceiveCount"],
        )
        messages: list[dict[str, Any]] = response.get("Messages", [])
        for message in messages:
            await self.__process_message(message)
        return len(messages)

    async def __process_message(self, message: dict[str, Any]) -> None:
        receipt_handle = message.get("ReceiptHandle")
        if not isinstance(receipt_handle, str) or not receipt_handle:
            _LOGGER.error("SQS work ingestion message has no receipt handle.")
            return

        try:
            ingestion_input = self.__parser.parse(message)
            claim = await self.__inbox.claim(
                ingestion_input.event_id,
                lease_seconds=self.__settings.visibility_timeout_seconds,
            )
        except Exception as error:
            await self.__schedule_retry(message, receipt_handle, error)
            return

        if claim.outcome is InboxClaimOutcome.ALREADY_PROCESSED:
            await self.__delete_message(
                receipt_handle,
                event_id=ingestion_input.event_id,
                duplicate=True,
            )
            return
        if claim.outcome is InboxClaimOutcome.BUSY:
            _LOGGER.info(
                "Work ingestion duplicate is already processing: "
                "event_id=%s attempt=%s",
                ingestion_input.event_id,
                claim.attempt,
            )
            return

        try:
            async with (
                SQSMessageVisibilityHeartbeat(
                    client=self.__client,
                    queue_url=self.__settings.queue_url,
                    receipt_handle=receipt_handle,
                    visibility_timeout_seconds=(
                        self.__settings.visibility_timeout_seconds
                    ),
                    interval_seconds=self.__settings.heartbeat_interval_seconds,
                ) as sqs_heartbeat,
                InboxClaimHeartbeat(
                    inbox=self.__inbox,
                    event_id=ingestion_input.event_id,
                    expected_attempt=claim.attempt,
                    lease_seconds=self.__settings.visibility_timeout_seconds,
                    interval_seconds=self.__settings.heartbeat_interval_seconds,
                ) as inbox_heartbeat,
            ):
                await self.__use_case.execute(ingestion_input)
                sqs_heartbeat.raise_if_failed()
                inbox_heartbeat.raise_if_failed()

            await self.__inbox.mark_processed(
                ingestion_input.event_id,
                expected_attempt=claim.attempt,
            )
        except Exception as error:
            try:
                updated = await self.__inbox.mark_failed(
                    ingestion_input.event_id,
                    expected_attempt=claim.attempt,
                    error_code=_failure_code(error),
                )
                if not updated:
                    _LOGGER.warning(
                        "Inbox failure was not recorded because the claim was lost: "
                        "event_id=%s attempt=%s",
                        ingestion_input.event_id,
                        claim.attempt,
                    )
            except Exception:
                _LOGGER.exception(
                    "Failed to persist inbox failure: event_id=%s attempt=%s",
                    ingestion_input.event_id,
                    claim.attempt,
                )
            await self.__schedule_retry(message, receipt_handle, error)
            return

        await self.__delete_message(
            receipt_handle,
            event_id=ingestion_input.event_id,
            duplicate=False,
        )
        _LOGGER.info(
            "Work ingestion message processed: event_id=%s ingestion_id=%s",
            ingestion_input.event_id,
            ingestion_input.ingestion_id.value,
        )

    async def __delete_message(
        self,
        receipt_handle: str,
        *,
        event_id: str,
        duplicate: bool,
    ) -> None:
        try:
            await asyncio.to_thread(
                self.__client.delete_message,
                QueueUrl=self.__settings.queue_url,
                ReceiptHandle=receipt_handle,
            )
            if duplicate:
                _LOGGER.info(
                    "Processed work ingestion duplicate acknowledged: event_id=%s",
                    event_id,
                )
        except Exception:
            _LOGGER.exception(
                "Failed to acknowledge processed work ingestion message: "
                "event_id=%s",
                event_id,
            )

    async def __schedule_retry(
        self,
        message: dict[str, Any],
        receipt_handle: str,
        error: Exception,
    ) -> None:
        receive_count = self.__receive_count(message)
        retry_delay = min(
            self.__settings.retry_base_seconds * (2 ** (receive_count - 1)),
            self.__settings.retry_max_seconds,
        )
        _LOGGER.error(
            "Work ingestion message failed: message_id=%s receive_count=%s "
            "error_type=%s error_code=%s",
            message.get("MessageId", "unknown"),
            receive_count,
            type(error).__name__,
            _failure_code(error),
        )
        try:
            await asyncio.to_thread(
                self.__client.change_message_visibility,
                QueueUrl=self.__settings.queue_url,
                ReceiptHandle=receipt_handle,
                VisibilityTimeout=retry_delay,
            )
        except Exception:
            _LOGGER.exception("Failed to schedule retry for work ingestion message.")

    @staticmethod
    def __receive_count(message: dict[str, Any]) -> int:
        try:
            return max(
                1,
                int(
                    message.get("Attributes", {}).get(
                        "ApproximateReceiveCount",
                        "1",
                    )
                ),
            )
        except (TypeError, ValueError):
            return 1


def _failure_code(error: Exception) -> str:
    code = getattr(error, "code", None)
    if isinstance(code, str) and code.strip():
        return code.strip()[:128]
    return type(error).__name__[:128]
