from __future__ import annotations

from types import TracebackType
from typing import Protocol, Self

from src.modules.ai_processing.domain.ports.repositories import (
    IInboxEventRepository,
    IWorkIngestionChunkRepository,
)


class IAIProcessingUnitOfWork(Protocol):
    @property
    def inbox_event_repository(self) -> IInboxEventRepository: ...

    @property
    def work_ingestion_chunk_repository(
        self,
    ) -> IWorkIngestionChunkRepository: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self) -> Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
