from dataclasses import dataclass
from datetime import datetime

from src.modules.ai_processing.application.dto import StorageObjectLocationDTO
from src.modules.auth.public import UserId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(frozen=True, slots=True)
class ProcessWorkIngestionInputDTO:
    event_id: str
    ingestion_id: WorkIngestionId
    work_id: WorkId
    requested_by: UserId
    source_document: StorageObjectLocationDTO
    occurred_at: datetime
    delivery_attempt: int = 1


@dataclass(frozen=True, slots=True)
class ProcessWorkIngestionOutputDTO:
    ingestion_id: WorkIngestionId
    total_chunks: int
    completed_chunks: int
