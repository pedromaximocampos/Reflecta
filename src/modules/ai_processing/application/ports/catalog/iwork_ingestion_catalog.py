from datetime import datetime
from typing import Protocol

from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


class IWorkIngestionCatalog(Protocol):
    async def mark_processing(
        self,
        ingestion_id: WorkIngestionId,
        *,
        now: datetime,
    ) -> bool:
        """Return False when the ingestion is already pending review/completed."""
        ...

    async def mark_pending_review(
        self,
        ingestion_id: WorkIngestionId,
        *,
        now: datetime,
    ) -> None: ...

    async def mark_failed(
        self,
        ingestion_id: WorkIngestionId,
        *,
        now: datetime,
        error_code: str,
        error_message: str,
    ) -> None: ...
