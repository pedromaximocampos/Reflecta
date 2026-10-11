import hashlib
import re
from dataclasses import dataclass

from src.modules.ai_processing.application.dto import (
    ChunkDraftDTO,
    NormalizedDocumentDTO,
    PageTextSpanDTO,
)
from src.modules.ai_processing.application.exceptions import WorkDocumentChunkingError
from src.modules.ai_processing.application.ports.document import ITextChunker


@dataclass(frozen=True, slots=True)
class _TokenSpan:
    start: int
    end: int
    value: str


class BoundaryAwareTextChunker(ITextChunker):
    """Creates overlapping chunks and prefers paragraph/sentence boundaries.

    Token counting is provider-neutral: words and punctuation are lexical tokens.
    The version records that choice so chunks can be regenerated deterministically
    when a model-specific tokenizer is adopted.
    """

    VERSION = "lexical-boundary-v1"
    _TOKEN_PATTERN = re.compile(r"\w+(?:['’]\w+)?|[^\w\s]", re.UNICODE)
    _SENTENCE_ENDINGS = frozenset(".!?…")

    def __init__(
        self,
        *,
        max_tokens: int = 900,
        min_tokens: int = 600,
        overlap_tokens: int = 150,
    ) -> None:
        if min_tokens <= 0 or max_tokens < min_tokens:
            raise ValueError("Chunk token limits are invalid.")
        if overlap_tokens < 0 or overlap_tokens >= min_tokens:
            raise ValueError("Chunk overlap must be smaller than the minimum size.")
        self._max_tokens = max_tokens
        self._min_tokens = min_tokens
        self._overlap_tokens = overlap_tokens

    def create_chunks(
        self,
        document: NormalizedDocumentDTO,
    ) -> tuple[ChunkDraftDTO, ...]:
        tokens = tuple(
            _TokenSpan(match.start(), match.end(), match.group(0))
            for match in self._TOKEN_PATTERN.finditer(document.text)
        )
        if not tokens:
            raise WorkDocumentChunkingError("The normalized document has no tokens.")

        paragraph_boundaries, sentence_boundaries = self._boundaries(
            document.text,
            tokens,
        )
        chunks: list[ChunkDraftDTO] = []
        start = 0
        while start < len(tokens):
            end = self._choose_end(
                start,
                len(tokens),
                paragraph_boundaries,
                sentence_boundaries,
            )
            start_offset = tokens[start].start
            end_offset = tokens[end - 1].end
            chunk_text = document.text[start_offset:end_offset]
            start_page, end_page = self._page_range(
                document.page_spans,
                start_offset,
                end_offset,
            )
            chunks.append(
                ChunkDraftDTO(
                    chunk_index=len(chunks),
                    start_page=start_page,
                    end_page=end_page,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    content_sha256=hashlib.sha256(
                        chunk_text.encode("utf-8")
                    ).hexdigest(),
                    chunker_version=self.VERSION,
                )
            )
            if end >= len(tokens):
                break
            start = self._choose_next_start(
                current_start=start,
                end=end,
                paragraph_boundaries=paragraph_boundaries,
                sentence_boundaries=sentence_boundaries,
            )
        return tuple(chunks)

    def _choose_end(
        self,
        start: int,
        total: int,
        paragraph_boundaries: set[int],
        sentence_boundaries: set[int],
    ) -> int:
        ideal = min(total, start + self._max_tokens)
        if ideal == total:
            return total
        minimum = min(ideal, start + self._min_tokens)
        return (
            self._last_boundary(paragraph_boundaries, minimum, ideal)
            or self._last_boundary(sentence_boundaries, minimum, ideal)
            or ideal
        )

    def _choose_next_start(
        self,
        *,
        current_start: int,
        end: int,
        paragraph_boundaries: set[int],
        sentence_boundaries: set[int],
    ) -> int:
        target = max(current_start + 1, end - self._overlap_tokens)
        candidate = (
            self._first_boundary(paragraph_boundaries, target, end)
            or self._first_boundary(sentence_boundaries, target, end)
            or target
        )
        return min(max(candidate, current_start + 1), end - 1)

    @classmethod
    def _boundaries(
        cls,
        text: str,
        tokens: tuple[_TokenSpan, ...],
    ) -> tuple[set[int], set[int]]:
        paragraph: set[int] = set()
        sentence: set[int] = set()
        for index in range(1, len(tokens)):
            separator = text[tokens[index - 1].end : tokens[index].start]
            if "\n\n" in separator:
                paragraph.add(index)
            if tokens[index - 1].value in cls._SENTENCE_ENDINGS:
                sentence.add(index)
        return paragraph, sentence

    @staticmethod
    def _last_boundary(boundaries: set[int], minimum: int, maximum: int) -> int:
        return max(
            (value for value in boundaries if minimum <= value <= maximum),
            default=0,
        )

    @staticmethod
    def _first_boundary(boundaries: set[int], minimum: int, maximum: int) -> int:
        return min(
            (value for value in boundaries if minimum <= value < maximum),
            default=0,
        )

    @staticmethod
    def _page_range(
        spans: tuple[PageTextSpanDTO, ...],
        start_offset: int,
        end_offset: int,
    ) -> tuple[int, int]:
        touched = [
            span.page_number
            for span in spans
            if span.end_offset > start_offset and span.start_offset < end_offset
        ]
        if not touched:
            raise WorkDocumentChunkingError(
                "Chunk offsets do not overlap any normalized page."
            )
        return touched[0], touched[-1]
