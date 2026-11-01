from dataclasses import dataclass
from datetime import datetime

from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.modules.catalog.public import WorkIngestionSummary


@dataclass(frozen=True, slots=True)
class WorkIngestionProgressOutputDTO:
    total: int
    pending: int
    processing: int
    completed: int
    failed: int
    percentage: int | None

    @classmethod
    def from_counts(
        cls,
        counts: dict[WorkIngestionChunkStatus, int],
    ) -> "WorkIngestionProgressOutputDTO":
        pending = counts.get(WorkIngestionChunkStatus.PENDING, 0)
        processing = counts.get(WorkIngestionChunkStatus.PROCESSING, 0)
        completed = counts.get(WorkIngestionChunkStatus.COMPLETED, 0)
        failed = counts.get(WorkIngestionChunkStatus.FAILED, 0)
        total = pending + processing + completed + failed
        percentage = None if total == 0 else round(completed * 100 / total)
        return cls(total, pending, processing, completed, failed, percentage)

    def to_dict(self) -> dict[str, int | None]:
        return {
            "total": self.total,
            "pending": self.pending,
            "processing": self.processing,
            "completed": self.completed,
            "failed": self.failed,
            "percentage": self.percentage,
        }


@dataclass(frozen=True, slots=True)
class WorkIngestionFailureOutputDTO:
    source: str
    failure_id: str
    code: str
    message: str
    occurred_at: str

    @classmethod
    def from_record(
        cls,
        record: dict[str, object] | None,
    ) -> "WorkIngestionFailureOutputDTO | None":
        if record is None:
            return None
        return cls(
            source=str(record["source"]),
            failure_id=str(record["id"]),
            code=str(record["code"]),
            message=str(record["message"]),
            occurred_at=str(record["occurred_at"]),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "failure_id": self.failure_id,
            "code": self.code,
            "message": self.message,
            "occurred_at": self.occurred_at,
        }


@dataclass(frozen=True, slots=True)
class WorkIngestionOutputDTO:
    ingestion_id: str
    work_id: str
    status: str
    attempts: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    error_code: str | None
    progress: WorkIngestionProgressOutputDTO
    failure: WorkIngestionFailureOutputDTO | None

    @classmethod
    def from_summary(
        cls,
        summary: WorkIngestionSummary,
        progress: WorkIngestionProgressOutputDTO,
        failure: WorkIngestionFailureOutputDTO | None,
    ) -> "WorkIngestionOutputDTO":
        return cls(
            ingestion_id=summary.ingestion_id.value,
            work_id=summary.work_id.value,
            status=summary.status,
            attempts=summary.attempts,
            created_at=summary.created_at,
            started_at=summary.started_at,
            finished_at=summary.finished_at,
            error_code=summary.error_code,
            progress=progress,
            failure=failure,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "ingestion_id": self.ingestion_id,
            "work_id": self.work_id,
            "status": self.status,
            "attempts": self.attempts,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": (
                self.finished_at.isoformat() if self.finished_at else None
            ),
            "error_code": self.error_code,
            "progress": self.progress.to_dict(),
            "failure": self.failure.to_dict() if self.failure else None,
        }


@dataclass(frozen=True, slots=True)
class WorkIngestionsOutputDTO:
    ingestions: tuple[WorkIngestionOutputDTO, ...]

    def to_dict(self) -> dict[str, list[dict[str, object]]]:
        return {"ingestions": [item.to_dict() for item in self.ingestions]}
