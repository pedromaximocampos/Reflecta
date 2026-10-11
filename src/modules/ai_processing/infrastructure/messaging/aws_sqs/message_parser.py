import json
from datetime import datetime
from typing import Any

from src.modules.ai_processing.application.dto import StorageObjectLocationDTO
from src.modules.ai_processing.application.use_cases.process_work_ingestion import (
    ProcessWorkIngestionInputDTO,
)
from src.modules.auth.public import UserId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


class WorkIngestionRequestedMessageParser:
    EVENT_TYPE = "catalog.work.ingestion.requested"

    def parse(self, message: dict[str, Any]) -> ProcessWorkIngestionInputDTO:
        body = message.get("Body")
        if not isinstance(body, str) or not body:
            raise ValueError("SQS work ingestion message body is missing.")
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as error:
            raise ValueError(
                "SQS work ingestion message body is invalid JSON."
            ) from error
        if not isinstance(payload, dict):
            raise ValueError("SQS work ingestion message body must be an object.")

        event_id = self._message_attribute(message, "id")
        event_type = self._message_attribute(message, "event_type")
        if event_type != self.EVENT_TYPE:
            raise ValueError(f"Unsupported event type '{event_type}'.")

        try:
            occurred_at = datetime.fromisoformat(str(payload["occurred_at"]))
            delivery_attempt = int(
                message.get("Attributes", {}).get("ApproximateReceiveCount", "1")
            )
            return ProcessWorkIngestionInputDTO(
                event_id=event_id,
                ingestion_id=WorkIngestionId(str(payload["ingestion_id"])),
                work_id=WorkId(str(payload["work_id"])),
                requested_by=UserId(str(payload["requested_by"])),
                source_document=StorageObjectLocationDTO(
                    bucket=str(payload["s3_bucket"]),
                    object_key=str(payload["s3_object_key"]),
                ),
                occurred_at=occurred_at,
                delivery_attempt=delivery_attempt,
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(
                "SQS work ingestion message payload is invalid."
            ) from error

    @staticmethod
    def _message_attribute(message: dict[str, Any], name: str) -> str:
        attributes = message.get("MessageAttributes", {})
        value = attributes.get(name, {}).get("StringValue")
        if not isinstance(value, str) or not value:
            raise ValueError(f"SQS message attribute '{name}' is missing.")
        return value
