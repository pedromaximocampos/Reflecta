from typing import Protocol

from src.modules.ai_processing.application.dto import (
    ExtractedDocumentDTO,
    NormalizedDocumentDTO,
)


class ITextNormalizer(Protocol):
    def normalize(self, document: ExtractedDocumentDTO) -> NormalizedDocumentDTO: ...
