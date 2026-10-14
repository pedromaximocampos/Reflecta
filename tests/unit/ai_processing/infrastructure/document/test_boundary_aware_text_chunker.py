import hashlib

from src.modules.ai_processing.application.dto import (
    NormalizedDocumentDTO,
    PageTextSpanDTO,
)
from src.modules.ai_processing.infrastructure.document import BoundaryAwareTextChunker


def test_chunker_creates_overlapping_deterministic_chunks_with_page_ranges() -> None:
    text = (
        "Primeira frase com algumas palavras. Segunda frase também possui palavras.\n\n"
        "Terceira frase cruza a página e mantém contexto. Quarta frase finaliza o texto."
    )
    split = text.index("Terceira")
    document = NormalizedDocumentDTO(
        text=text,
        page_spans=(
            PageTextSpanDTO(1, 0, split - 2),
            PageTextSpanDTO(2, split, len(text)),
        ),
        content_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        normalizer_version="test-v1",
    )
    chunker = BoundaryAwareTextChunker(
        min_tokens=8,
        max_tokens=14,
        overlap_tokens=3,
    )

    chunks = chunker.create_chunks(document)

    assert len(chunks) >= 2
    assert [chunk.chunk_index for chunk in chunks] == list(range(len(chunks)))
    assert chunks[1].start_offset < chunks[0].end_offset
    for chunk in chunks:
        content = text[chunk.start_offset : chunk.end_offset]
        assert (
            chunk.content_sha256 == hashlib.sha256(content.encode("utf-8")).hexdigest()
        )
        assert chunk.start_page <= chunk.end_page
        assert chunk.chunker_version == "lexical-boundary-v1"
