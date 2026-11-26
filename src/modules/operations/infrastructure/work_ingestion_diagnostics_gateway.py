import asyncio
import hashlib
import re
from datetime import datetime, timedelta
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy import select

from src.modules.ai_processing.application.dto import StorageObjectLocationDTO
from src.modules.ai_processing.application.ports.storage import IWorkIngestionStorage
from src.modules.ai_processing.infrastructure.persistence.postgresql.models import (
    WorkIngestionChunkModel,
    WorkIngestionFailureAttemptModel,
)
from src.modules.catalog.infrastructure.persistence.postgresql.models.work_ingestion_model import (
    WorkIngestionModel,
)
from src.modules.operations.infrastructure.failure_gateway import failure_rows


_STREAMS = {
    "journal": "worker-journal-analysis",
    "work_ingestion": "worker-work-ingestion",
    "work_chunk": "worker-work-ingestion",
    "inbox": "worker-work-ingestion",
    "outbox": "worker-outbox-dispatcher",
}
_SAFE_IDENTIFIER = re.compile(r"^[A-Za-z0-9_:.\-/]{1,300}$")
_SECRET_PATTERNS = (
    (re.compile(r"\bsk-[A-Za-z0-9_-]+\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+\-/]+=*"), "Bearer [REDACTED]"),
    (re.compile(r"(?i)\b(password|secret|token)=\S+"), r"\1=[REDACTED]"),
)


class WorkIngestionFailureContextGateway:
    def __init__(self, db, storage: IWorkIngestionStorage) -> None:
        self._db = db
        self._storage = storage

    async def get_context(self, source: str, failure_id: str) -> dict[str, Any] | None:
        rows = failure_rows()
        async with self._db.session() as session:
            row = (
                await session.execute(
                    select(rows).where(
                        rows.c.source == source,
                        rows.c.id == failure_id,
                    )
                )
            ).mappings().one_or_none()
            if row is None:
                return None
            ingestion_id = (
                row["entity_id"] if source == "work_ingestion" else row["related_id"]
            )
            if not ingestion_id:
                return {"available": False, "reason": "no_work_ingestion"}
            ingestion = await session.get(WorkIngestionModel, ingestion_id)
            if ingestion is None:
                return None
            attempt_query = select(WorkIngestionFailureAttemptModel).where(
                WorkIngestionFailureAttemptModel.ingestion_id == ingestion_id
            )
            if source == "work_chunk":
                attempt_query = attempt_query.where(
                    WorkIngestionFailureAttemptModel.chunk_id == row["entity_id"]
                )
            attempt = await session.scalar(
                attempt_query.order_by(
                    WorkIngestionFailureAttemptModel.occurred_at.desc(),
                    WorkIngestionFailureAttemptModel.id.desc(),
                ).limit(1)
            )
            chunk = None
            chunk_id = attempt.chunk_id if attempt is not None else (
                row["entity_id"] if source == "work_chunk" else None
            )
            if chunk_id:
                chunk = await session.get(WorkIngestionChunkModel, chunk_id)

        base = {
            "available": chunk is not None,
            "ingestion_id": ingestion.id,
            "chunk_id": chunk.id if chunk is not None else None,
            "stage": attempt.stage if attempt is not None else None,
            "attempt": attempt.attempt if attempt is not None else row["attempts"],
            "error_code": attempt.error_code if attempt is not None else row["code"],
            "error_message": attempt.error_message if attempt is not None else row["message"],
        }
        if chunk is None:
            return {
                **base,
                "reason": "failure_before_chunk_creation",
                "message": "A falha ocorreu antes da criação de um trecho. Abra o PDF original para inspecionar a entrada.",
            }

        if attempt is not None and attempt.context_text is not None:
            return {
                **base,
                "start_page": attempt.start_page,
                "end_page": attempt.end_page,
                "start_offset": attempt.start_offset,
                "end_offset": attempt.end_offset,
                "content_sha256": attempt.content_sha256,
                "text": attempt.context_text,
                "source": "failure_snapshot",
            }

        normalized_location = StorageObjectLocationDTO(
            bucket=ingestion.s3_bucket,
            object_key=(
                f"works/{ingestion.work_id}/processing/{ingestion.id}/normalized.txt"
            ),
        )
        text = await self._storage.load_normalized_text(location=normalized_location)
        if chunk.end_offset > len(text):
            return {**base, "available": False, "reason": "invalid_chunk_offsets"}
        chunk_text = text[chunk.start_offset : chunk.end_offset]
        digest = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
        if digest != chunk.content_sha256:
            return {**base, "available": False, "reason": "chunk_checksum_mismatch"}
        return {
            **base,
            "start_page": chunk.start_page,
            "end_page": chunk.end_page,
            "start_offset": chunk.start_offset,
            "end_offset": chunk.end_offset,
            "content_sha256": chunk.content_sha256,
            "text": chunk_text,
            "source": "normalized_document",
        }


class CloudWatchOperationalLogGateway:
    def __init__(
        self,
        *,
        aws_region: str,
        log_group: str,
        aws_profile: str | None = None,
    ) -> None:
        session = (
            boto3.Session(profile_name=aws_profile, region_name=aws_region)
            if aws_profile
            else boto3.Session(region_name=aws_region)
        )
        self._client = session.client("logs")
        self._log_group = log_group

    async def list_logs(self, detail: dict[str, Any]) -> dict[str, Any]:
        source = str(detail["source"])
        stream = _STREAMS.get(source)
        if stream is None:
            return {"logs": [], "retention_days": 14}
        occurred_at = datetime.fromisoformat(str(detail["occurred_at"]))
        if occurred_at.tzinfo is None:
            raise ValueError("Failure occurrence must include a timezone.")
        attempt = detail.get("failure_attempt") or {}
        identifiers = {
            str(value)
            for value in (
                detail.get("id"),
                detail.get("entity_id"),
                detail.get("related_id"),
                attempt.get("id"),
                attempt.get("ingestion_id"),
                attempt.get("chunk_id"),
                attempt.get("provider_request_id"),
                attempt.get("provider_response_id"),
            )
            if value and _SAFE_IDENTIFIER.fullmatch(str(value))
        }
        start_ms = int((occurred_at - timedelta(minutes=5)).timestamp() * 1000)
        end_ms = int((occurred_at + timedelta(minutes=5)).timestamp() * 1000)
        responses = await asyncio.gather(
            *(
                asyncio.to_thread(
                    self._client.filter_log_events,
                    logGroupName=self._log_group,
                    logStreamNames=[stream],
                    startTime=start_ms,
                    endTime=end_ms,
                    filterPattern=f'"{identifier}"',
                    limit=100,
                )
                for identifier in sorted(identifiers)
            )
        )
        unique: dict[str, dict[str, Any]] = {}
        for response in responses:
            for event in response.get("events", []):
                event_id = str(event.get("eventId") or f"{event.get('timestamp')}:{event.get('message')}")
                unique[event_id] = {
                    "timestamp": datetime.fromtimestamp(
                        int(event["timestamp"]) / 1000,
                        tz=occurred_at.tzinfo,
                    ).isoformat(),
                    "stream": stream,
                    "message": _sanitize_message(str(event.get("message", ""))),
                }
        logs = sorted(unique.values(), key=lambda item: item["timestamp"])[-100:]
        return {"logs": logs, "retention_days": 14}


def _sanitize_message(message: str) -> str:
    sanitized = message[:2000]
    for pattern, replacement in _SECRET_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized


__all__ = (
    "BotoCoreError",
    "ClientError",
    "CloudWatchOperationalLogGateway",
    "WorkIngestionFailureContextGateway",
)
