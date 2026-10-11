from dataclasses import dataclass
from datetime import datetime

from src.modules.ai_processing.domain.value_objects import InboxEventStatus


@dataclass(eq=False, slots=True)
class InboxEvent:
    consumer_name: str
    event_id: str
    status: InboxEventStatus
    attempts: int
    received_at: datetime
    updated_at: datetime
    lease_expires_at: datetime | None = None
    processed_at: datetime | None = None
    error_code: str | None = None
    error_message: str | None = None

    def __post_init__(self) -> None:
        if not self.consumer_name.strip() or len(self.consumer_name) > 128:
            raise ValueError("Inbox consumer name must contain at most 128 characters.")
        if not self.event_id.strip() or len(self.event_id) > 128:
            raise ValueError("Inbox event ID must contain at most 128 characters.")
        if self.attempts < 1:
            raise ValueError("Inbox attempts must be greater than zero.")

    def has_active_lease(self, *, now: datetime) -> bool:
        return (
            self.status is InboxEventStatus.PROCESSING
            and self.lease_expires_at is not None
            and self.lease_expires_at > now
        )

    def restart_processing(
        self,
        *,
        now: datetime,
        lease_expires_at: datetime,
    ) -> None:
        if self.status is InboxEventStatus.PROCESSED:
            raise ValueError("A processed inbox event cannot be reclaimed.")
        if self.has_active_lease(now=now):
            raise ValueError("An active inbox event lease cannot be reclaimed.")
        self._validate_future_lease(now, lease_expires_at)
        self.status = InboxEventStatus.PROCESSING
        self.attempts += 1
        self.updated_at = now
        self.lease_expires_at = lease_expires_at
        self.processed_at = None
        self.error_code = None
        self.error_message = None

    def mark_processed(self, *, now: datetime) -> None:
        self._ensure_processing()
        self.status = InboxEventStatus.PROCESSED
        self.updated_at = now
        self.lease_expires_at = None
        self.processed_at = now
        self.error_code = None
        self.error_message = None

    def mark_failed(
        self,
        *,
        now: datetime,
        error_code: str,
        error_message: str,
    ) -> None:
        self._ensure_processing()
        if not error_code.strip() or not error_message.strip():
            raise ValueError("Inbox failure code and message must not be empty.")
        self.status = InboxEventStatus.FAILED
        self.updated_at = now
        self.lease_expires_at = None
        self.processed_at = None
        self.error_code = error_code
        self.error_message = error_message

    @staticmethod
    def _validate_future_lease(now: datetime, lease_expires_at: datetime) -> None:
        if lease_expires_at <= now:
            raise ValueError("Inbox processing lease must expire in the future.")

    def _ensure_processing(self) -> None:
        if self.status is not InboxEventStatus.PROCESSING:
            raise ValueError("Inbox event must be processing for this transition.")
