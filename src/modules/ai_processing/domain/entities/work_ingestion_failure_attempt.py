from dataclasses import dataclass
from datetime import datetime

from src.modules.ai_processing.public import WorkIngestionChunkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(frozen=True, slots=True)
class WorkIngestionFailureAttempt:
    id: str
    ingestion_id: WorkIngestionId
    chunk_id: WorkIngestionChunkId | None
    stage: str
    attempt: int
    error_code: str
    error_message: str
    occurred_at: datetime
    start_page: int | None = None
    end_page: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    content_sha256: str | None = None
    provider_request_id: str | None = None
    provider_response_id: str | None = None
    context_text: str | None = None

    def __post_init__(self) -> None:
        if len(self.id) != 26 or not self.id.strip():
            raise ValueError("Failure attempt ID must be a 26-character ULID.")
        if not self.stage.strip() or len(self.stage) > 64:
            raise ValueError("Failure stage must contain at most 64 characters.")
        if self.attempt < 1:
            raise ValueError("Failure attempt must be positive.")
        if not self.error_code.strip() or len(self.error_code) > 128:
            raise ValueError("Failure code must contain at most 128 characters.")
        if not self.error_message.strip() or len(self.error_message) > 2000:
            raise ValueError("Failure message must contain at most 2000 characters.")
