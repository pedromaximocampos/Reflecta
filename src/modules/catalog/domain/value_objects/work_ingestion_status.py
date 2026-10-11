from enum import Enum


class WorkIngestionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PENDING_REVIEW = "pending_review"
    COMPLETED = "completed"
    FAILED = "failed"
