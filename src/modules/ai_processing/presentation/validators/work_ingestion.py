from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class WorkIngestionProgressValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int = Field(ge=0)
    pending: int = Field(ge=0)
    processing: int = Field(ge=0)
    completed: int = Field(ge=0)
    failed: int = Field(ge=0)
    percentage: int | None = Field(default=None, ge=0, le=100)


class WorkIngestionValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ingestion_id: str = Field(min_length=26, max_length=26)
    work_id: str = Field(min_length=26, max_length=26)
    status: Literal[
        "pending",
        "processing",
        "pending_review",
        "completed",
        "failed",
    ]
    attempts: int = Field(ge=0)
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_code: str | None = None
    progress: WorkIngestionProgressValidator


class WorkIngestionsResponseValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ingestions: list[WorkIngestionValidator]
