from dataclasses import dataclass
from datetime import datetime

from src.modules.auth.public.user_id import UserId
from src.modules.catalog.domain.exceptions.work_exceptions import (
    InvalidWorkIngestionTransitionError,
)
from src.modules.catalog.domain.value_objects.work_ingestion_status import (
    WorkIngestionStatus,
)
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(eq=False, slots=True)
class WorkIngestion:
    id: WorkIngestionId
    work_id: WorkId
    requested_by: UserId
    document_location: WorkDocumentLocation
    created_at: datetime
    status: WorkIngestionStatus = WorkIngestionStatus.PENDING
    attempts: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None

    def mark_processing(self, *, now: datetime) -> None:
        self._ensure_transition_to(
            WorkIngestionStatus.PROCESSING,
            allowed_from={WorkIngestionStatus.PENDING, WorkIngestionStatus.FAILED},
        )
        self.status = WorkIngestionStatus.PROCESSING
        self.attempts += 1
        self.started_at = now
        self.finished_at = None
        self.error_code = None
        self.error_message = None

    def mark_pending_review(self, *, now: datetime) -> None:
        self._ensure_transition_to(
            WorkIngestionStatus.PENDING_REVIEW,
            allowed_from={
                WorkIngestionStatus.PROCESSING,
                WorkIngestionStatus.FAILED,
            },
        )
        self.status = WorkIngestionStatus.PENDING_REVIEW
        self.finished_at = now
        self.error_code = None
        self.error_message = None

    def mark_completed(self, *, now: datetime) -> None:
        self._ensure_transition_to(
            WorkIngestionStatus.COMPLETED,
            allowed_from={WorkIngestionStatus.PENDING_REVIEW},
        )
        self.status = WorkIngestionStatus.COMPLETED
        self.finished_at = self.finished_at or now

    def mark_failed(
        self,
        *,
        now: datetime,
        error_code: str,
        error_message: str,
    ) -> None:
        self._ensure_transition_to(
            WorkIngestionStatus.FAILED,
            allowed_from={WorkIngestionStatus.PROCESSING},
        )
        self.status = WorkIngestionStatus.FAILED
        self.finished_at = now
        self.error_code = error_code
        self.error_message = error_message

    def _ensure_transition_to(
        self,
        target: WorkIngestionStatus,
        *,
        allowed_from: set[WorkIngestionStatus],
    ) -> None:
        if self.status not in allowed_from:
            raise InvalidWorkIngestionTransitionError(
                current_status=self.status.value,
                target_status=target.value,
            )
