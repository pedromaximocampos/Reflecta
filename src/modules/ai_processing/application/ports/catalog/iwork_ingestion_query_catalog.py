from typing import Protocol

from src.modules.catalog.public import WorkIngestionSummary


class IWorkIngestionQueryCatalog(Protocol):
    async def list_recent(
        self,
        *,
        limit: int,
    ) -> tuple[WorkIngestionSummary, ...]: ...
