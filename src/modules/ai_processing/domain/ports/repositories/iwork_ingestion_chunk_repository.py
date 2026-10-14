from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from src.modules.ai_processing.domain.entities import WorkIngestionChunk
from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.modules.ai_processing.public import WorkIngestionChunkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


class IWorkIngestionChunkRepository(Protocol):
    async def create_many(
        self,
        chunks: Sequence[WorkIngestionChunk],
    ) -> tuple[WorkIngestionChunk, ...]: ...

    async def find_by_id(
        self,
        chunk_id: WorkIngestionChunkId,
    ) -> WorkIngestionChunk | None: ...

    async def list_by_ingestion(
        self,
        ingestion_id: WorkIngestionId,
        *,
        statuses: set[WorkIngestionChunkStatus] | None = None,
    ) -> tuple[WorkIngestionChunk, ...]: ...

    async def claim_next(
        self,
        ingestion_id: WorkIngestionId,
        *,
        now: datetime,
        lease_expires_at: datetime,
    ) -> WorkIngestionChunk | None: ...

    async def update(
        self,
        chunk: WorkIngestionChunk,
    ) -> WorkIngestionChunk: ...

    async def update_claimed(
        self,
        chunk: WorkIngestionChunk,
        *,
        expected_attempts: int,
    ) -> WorkIngestionChunk | None: ...

    async def count_by_status(
        self,
        ingestion_id: WorkIngestionId,
    ) -> dict[WorkIngestionChunkStatus, int]: ...
