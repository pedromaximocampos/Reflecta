from typing import Protocol

from src.modules.ai_processing.application.dto import (
    ChunkDraftDTO,
    NormalizedDocumentDTO,
)


class ITextChunker(Protocol):
    def create_chunks(
        self,
        document: NormalizedDocumentDTO,
    ) -> tuple[ChunkDraftDTO, ...]: ...
