from typing import BinaryIO, Protocol

from src.modules.ai_processing.application.dto import ExtractedDocumentDTO


class IWorkDocumentTextExtractor(Protocol):
    async def extract(self, document: BinaryIO) -> ExtractedDocumentDTO: ...
