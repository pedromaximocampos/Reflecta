import hashlib
import math
import re
import unicodedata
from collections import Counter

from src.modules.ai_processing.application.dto import (
    ExtractedDocumentDTO,
    NormalizedDocumentDTO,
    PageTextSpanDTO,
)
from src.modules.ai_processing.application.exceptions import (
    WorkDocumentNormalizationError,
)
from src.modules.ai_processing.application.ports.document import ITextNormalizer


class UnicodeTextNormalizer(ITextNormalizer):
    VERSION = "unicode-v1"
    _SPACE_PATTERN = re.compile(r"[\t\f\v ]+")
    _PARAGRAPH_PATTERN = re.compile(r"\n\s*\n+")
    _DEHYPHENATION_PATTERN = re.compile(r"(?<=\w)-\n(?=[a-zà-öø-ÿ])")
    _ZERO_WIDTH_PATTERN = re.compile(r"[\u200b-\u200d\ufeff\x00]")
    _TERMINAL_PUNCTUATION = frozenset(".!?…:;\"'”’)]}")

    def normalize(self, document: ExtractedDocumentDTO) -> NormalizedDocumentDTO:
        if not document.pages:
            raise WorkDocumentNormalizationError("The document has no pages.")

        raw_lines = [self._clean_lines(page.text) for page in document.pages]
        repeated_headers, repeated_footers = self._repeated_marginal_lines(raw_lines)
        normalized_pages: list[tuple[int, str]] = []

        for page, lines in zip(document.pages, raw_lines, strict=True):
            content_lines = self._remove_repeated_margins(
                lines,
                repeated_headers,
                repeated_footers,
            )
            text = self._normalize_page("\n".join(content_lines))
            if text:
                normalized_pages.append((page.page_number, text))

        if not normalized_pages:
            raise WorkDocumentNormalizationError(
                "The document has no text after normalization."
            )

        parts: list[str] = []
        spans: list[PageTextSpanDTO] = []
        current_offset = 0
        previous_text = ""
        for page_number, page_text in normalized_pages:
            separator = self._page_separator(previous_text, page_text) if parts else ""
            if separator:
                parts.append(separator)
                current_offset += len(separator)
            start_offset = current_offset
            parts.append(page_text)
            current_offset += len(page_text)
            spans.append(
                PageTextSpanDTO(
                    page_number=page_number,
                    start_offset=start_offset,
                    end_offset=current_offset,
                )
            )
            previous_text = page_text

        text = "".join(parts)
        return NormalizedDocumentDTO(
            text=text,
            page_spans=tuple(spans),
            content_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            normalizer_version=self.VERSION,
        )

    def _clean_lines(self, text: str) -> list[str]:
        text = unicodedata.normalize("NFC", text or "")
        text = self._ZERO_WIDTH_PATTERN.sub("", text)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        return [self._SPACE_PATTERN.sub(" ", line).strip() for line in text.split("\n")]

    @classmethod
    def _repeated_marginal_lines(
        cls,
        pages: list[list[str]],
    ) -> tuple[set[str], set[str]]:
        if len(pages) < 3:
            return set(), set()
        threshold = max(3, math.ceil(len(pages) * 0.6))
        headers = Counter(cls._first_non_empty(lines) for lines in pages)
        footers = Counter(cls._last_non_empty(lines) for lines in pages)
        headers.pop(None, None)
        footers.pop(None, None)
        return (
            {line for line, count in headers.items() if count >= threshold},
            {line for line, count in footers.items() if count >= threshold},
        )

    @staticmethod
    def _first_non_empty(lines: list[str]) -> str | None:
        return next((line.casefold() for line in lines if line), None)

    @staticmethod
    def _last_non_empty(lines: list[str]) -> str | None:
        return next((line.casefold() for line in reversed(lines) if line), None)

    @classmethod
    def _remove_repeated_margins(
        cls,
        lines: list[str],
        headers: set[str],
        footers: set[str],
    ) -> list[str]:
        result = list(lines)
        first = next((index for index, line in enumerate(result) if line), None)
        if first is not None and result[first].casefold() in headers:
            result[first] = ""
        last = next(
            (index for index in range(len(result) - 1, -1, -1) if result[index]),
            None,
        )
        if last is not None and result[last].casefold() in footers:
            result[last] = ""
        return result

    def _normalize_page(self, text: str) -> str:
        text = self._DEHYPHENATION_PATTERN.sub("", text)
        paragraphs = []
        for paragraph in self._PARAGRAPH_PATTERN.split(text):
            joined = self._SPACE_PATTERN.sub(" ", paragraph.replace("\n", " ")).strip()
            if joined:
                paragraphs.append(joined)
        return "\n\n".join(paragraphs)

    def _page_separator(self, previous: str, current: str) -> str:
        if not previous or not current:
            return "\n\n"
        if previous[-1] not in self._TERMINAL_PUNCTUATION and current[0].islower():
            return " "
        return "\n\n"
