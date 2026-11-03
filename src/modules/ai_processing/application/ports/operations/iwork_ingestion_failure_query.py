from typing import Mapping, Protocol

from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


class IWorkIngestionFailureQuery(Protocol):
    async def latest_active_for_ingestions(
        self,
        ingestion_ids: tuple[WorkIngestionId, ...],
    ) -> Mapping[str, dict[str, object]]: ...
