import hashlib

from src.modules.ai_processing.application.dto import (
    ExtractedDocumentDTO,
    ExtractedPageDTO,
)
from src.modules.ai_processing.infrastructure.document import UnicodeTextNormalizer


def test_normalizer_removes_repeated_margins_and_preserves_page_spans() -> None:
    document = ExtractedDocumentDTO(
        pages=(
            ExtractedPageDTO(1, "REFLECTA\nA refle-\nxão continua\nPUBLIC DOMAIN"),
            ExtractedPageDTO(
                2, "REFLECTA\nentre páginas sem se perder.\nPUBLIC DOMAIN"
            ),
            ExtractedPageDTO(3, "REFLECTA\nOutro parágrafo termina.\nPUBLIC DOMAIN"),
        )
    )

    normalized = UnicodeTextNormalizer().normalize(document)

    assert "REFLECTA" not in normalized.text
    assert "PUBLIC DOMAIN" not in normalized.text
    assert "A reflexão continua entre páginas sem se perder." in normalized.text
    assert tuple(span.page_number for span in normalized.page_spans) == (1, 2, 3)
    assert (
        normalized.content_sha256
        == hashlib.sha256(normalized.text.encode("utf-8")).hexdigest()
    )
    assert normalized.normalizer_version == "unicode-v1"
