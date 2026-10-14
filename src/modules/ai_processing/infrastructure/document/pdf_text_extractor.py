import asyncio
from typing import BinaryIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from src.modules.ai_processing.application.dto import (
    ExtractedDocumentDTO,
    ExtractedPageDTO,
)
from src.modules.ai_processing.application.exceptions import (
    WorkDocumentExtractionError,
)
from src.modules.ai_processing.application.ports.document import (
    IWorkDocumentTextExtractor,
)


class PDFWorkDocumentTextExtractor(IWorkDocumentTextExtractor):
    """Extracts text page by page while keeping the original page number."""

    async def extract(self, document: BinaryIO) -> ExtractedDocumentDTO:
        try:
            return await asyncio.to_thread(self._extract_sync, document)
        except WorkDocumentExtractionError:
            raise
        except (OSError, PdfReadError, ValueError) as error:
            raise WorkDocumentExtractionError("The PDF could not be read.") from error

    @staticmethod
    def _extract_sync(document: BinaryIO) -> ExtractedDocumentDTO:
        if document.seekable():
            document.seek(0)
        reader = PdfReader(document, strict=False)
        if reader.is_encrypted and not reader.decrypt(""):
            raise WorkDocumentExtractionError(
                "Password-protected PDFs are not supported."
            )

        pages = tuple(
            ExtractedPageDTO(
                page_number=page_number,
                text=page.extract_text() or "",
            )
            for page_number, page in enumerate(reader.pages, start=1)
        )
        if not pages:
            raise WorkDocumentExtractionError("The PDF has no pages.")
        if not any(page.text.strip() for page in pages):
            raise WorkDocumentExtractionError(
                "The PDF has no extractable text; OCR is not available in this version."
            )
        return ExtractedDocumentDTO(pages=pages)
