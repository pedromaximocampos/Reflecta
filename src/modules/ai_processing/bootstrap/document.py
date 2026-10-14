from src.modules.ai_processing.infrastructure.document import (
    BoundaryAwareTextChunker,
    PDFWorkDocumentTextExtractor,
    UnicodeTextNormalizer,
)
from src.shared.config.settings import get_settings


def get_document_text_extractor() -> PDFWorkDocumentTextExtractor:
    return PDFWorkDocumentTextExtractor()


def get_text_normalizer() -> UnicodeTextNormalizer:
    return UnicodeTextNormalizer()


def get_text_chunker() -> BoundaryAwareTextChunker:
    settings = get_settings()
    return BoundaryAwareTextChunker(
        min_tokens=settings.AI_WORK_INGESTION_CHUNK_MIN_TOKENS,
        max_tokens=settings.AI_WORK_INGESTION_CHUNK_MAX_TOKENS,
        overlap_tokens=settings.AI_WORK_INGESTION_CHUNK_OVERLAP_TOKENS,
    )
