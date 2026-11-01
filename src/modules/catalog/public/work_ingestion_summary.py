from dataclasses import dataclass
from datetime import datetime

from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(frozen=True, slots=True)
class WorkIngestionSummary:
    ingestion_id: WorkIngestionId
    work_id: WorkId
    status: str
    attempts: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    error_code: str | None
