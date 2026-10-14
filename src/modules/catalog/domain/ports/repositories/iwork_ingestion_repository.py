from typing import Protocol

from src.modules.catalog.domain.entities.work_ingestion import WorkIngestion
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


class IWorkIngestionRepository(Protocol):
    async def create(self, ingestion: WorkIngestion) -> WorkIngestion: ...

    async def find_by_id(
        self,
        ingestion_id: WorkIngestionId,
    ) -> WorkIngestion | None: ...

    async def update(self, ingestion: WorkIngestion) -> WorkIngestion: ...
