from typing import BinaryIO, Protocol

from src.modules.catalog.application.dto import ProcessedWorkCoverDTO


class IWorkCoverProcessor(Protocol):
    async def process(
        self,
        *,
        content: BinaryIO,
        declared_content_type: str,
        declared_size_bytes: int,
    ) -> ProcessedWorkCoverDTO: ...
