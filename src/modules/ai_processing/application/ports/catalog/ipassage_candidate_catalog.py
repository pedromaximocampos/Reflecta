from typing import Protocol

from src.modules.catalog.public.passage_candidate import PassageSuggestion
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


class IPassageCandidateCatalog(Protocol):
    async def replace_chunk_suggestions(
        self,
        *,
        ingestion_id: WorkIngestionId,
        work_id: WorkId,
        chunk_id: str,
        suggestions: tuple[PassageSuggestion, ...],
    ) -> None: ...
