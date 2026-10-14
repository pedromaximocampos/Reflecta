from dataclasses import dataclass
from datetime import datetime

from src.modules.ai_processing.domain.exceptions import (
    InvalidWorkIngestionChunkError,
    InvalidWorkIngestionChunkTransitionError,
)
from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.modules.ai_processing.public import WorkIngestionChunkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(eq=False, slots=True)
class WorkIngestionChunk:
    id: WorkIngestionChunkId
    ingestion_id: WorkIngestionId
    chunk_index: int
    start_page: int
    end_page: int
    start_offset: int
    end_offset: int
    content_sha256: str
    chunker_version: str
    created_at: datetime
    updated_at: datetime
    status: WorkIngestionChunkStatus = WorkIngestionChunkStatus.PENDING
    attempts: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None
    lease_expires_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if self.chunk_index < 0:
            raise InvalidWorkIngestionChunkError(
                "Chunk index must be greater than or equal to zero."
            )
        if self.start_page < 1 or self.end_page < self.start_page:
            raise InvalidWorkIngestionChunkError("Chunk page range is invalid.")
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise InvalidWorkIngestionChunkError("Chunk text offsets are invalid.")
        if len(self.content_sha256) != 64:
            raise InvalidWorkIngestionChunkError(
                "Chunk content SHA-256 must contain 64 hexadecimal characters."
            )
        try:
            int(self.content_sha256, 16)
        except ValueError as error:
            raise InvalidWorkIngestionChunkError(
                "Chunk content SHA-256 must be hexadecimal."
            ) from error
        if not self.chunker_version.strip():
            raise InvalidWorkIngestionChunkError("Chunker version must not be empty.")
        if self.attempts < 0:
            raise InvalidWorkIngestionChunkError(
                "Chunk attempts must be greater than or equal to zero."
            )

    def mark_processing(
        self,
        *,
        now: datetime,
        lease_expires_at: datetime,
    ) -> None:
        can_reclaim = (
            self.status is WorkIngestionChunkStatus.PROCESSING
            and self.lease_expires_at is not None
            and self.lease_expires_at <= now
        )
        if (
            self.status
            not in {
                WorkIngestionChunkStatus.PENDING,
                WorkIngestionChunkStatus.FAILED,
            }
            and not can_reclaim
        ):
            self._raise_invalid_transition(WorkIngestionChunkStatus.PROCESSING)
        if lease_expires_at <= now:
            raise InvalidWorkIngestionChunkError(
                "Chunk processing lease must expire in the future."
            )

        self.status = WorkIngestionChunkStatus.PROCESSING
        self.attempts += 1
        self.started_at = now
        self.finished_at = None
        self.lease_expires_at = lease_expires_at
        self.error_code = None
        self.error_message = None
        self.updated_at = now

    def renew_lease(
        self,
        *,
        now: datetime,
        lease_expires_at: datetime,
    ) -> None:
        if self.status is not WorkIngestionChunkStatus.PROCESSING:
            self._raise_invalid_transition(WorkIngestionChunkStatus.PROCESSING)
        if lease_expires_at <= now:
            raise InvalidWorkIngestionChunkError(
                "Chunk processing lease must expire in the future."
            )
        self.lease_expires_at = lease_expires_at
        self.updated_at = now

    def mark_completed(self, *, now: datetime) -> None:
        if self.status is not WorkIngestionChunkStatus.PROCESSING:
            self._raise_invalid_transition(WorkIngestionChunkStatus.COMPLETED)
        self.status = WorkIngestionChunkStatus.COMPLETED
        self.finished_at = now
        self.lease_expires_at = None
        self.error_code = None
        self.error_message = None
        self.updated_at = now

    def mark_failed(
        self,
        *,
        now: datetime,
        error_code: str,
        error_message: str,
    ) -> None:
        if self.status is not WorkIngestionChunkStatus.PROCESSING:
            self._raise_invalid_transition(WorkIngestionChunkStatus.FAILED)
        if not error_code.strip() or not error_message.strip():
            raise InvalidWorkIngestionChunkError(
                "Chunk failure code and message must not be empty."
            )
        self.status = WorkIngestionChunkStatus.FAILED
        self.finished_at = now
        self.lease_expires_at = None
        self.error_code = error_code
        self.error_message = error_message
        self.updated_at = now

    def _raise_invalid_transition(
        self,
        target: WorkIngestionChunkStatus,
    ) -> None:
        raise InvalidWorkIngestionChunkTransitionError(
            current_status=self.status.value,
            target_status=target.value,
        )
