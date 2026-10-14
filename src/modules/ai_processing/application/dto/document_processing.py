from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractedPageDTO:
    page_number: int
    text: str

    def __post_init__(self) -> None:
        if self.page_number < 1:
            raise ValueError("Extracted page number must be positive.")


@dataclass(frozen=True, slots=True)
class ExtractedDocumentDTO:
    pages: tuple[ExtractedPageDTO, ...]

    def __post_init__(self) -> None:
        numbers = tuple(page.page_number for page in self.pages)
        if len(numbers) != len(set(numbers)):
            raise ValueError("Extracted page numbers must be unique.")


@dataclass(frozen=True, slots=True)
class PageTextSpanDTO:
    page_number: int
    start_offset: int
    end_offset: int

    def __post_init__(self) -> None:
        if self.page_number < 1 or self.start_offset < 0:
            raise ValueError("Normalized page span is invalid.")
        if self.end_offset <= self.start_offset:
            raise ValueError("Normalized page span must not be empty.")


@dataclass(frozen=True, slots=True)
class NormalizedDocumentDTO:
    text: str
    page_spans: tuple[PageTextSpanDTO, ...]
    content_sha256: str
    normalizer_version: str

    def __post_init__(self) -> None:
        if not self.text or not self.page_spans:
            raise ValueError("Normalized document must contain text and page spans.")
        if len(self.content_sha256) != 64:
            raise ValueError("Normalized document SHA-256 must contain 64 characters.")
        if not self.normalizer_version.strip():
            raise ValueError("Normalizer version must not be empty.")


@dataclass(frozen=True, slots=True)
class ChunkDraftDTO:
    chunk_index: int
    start_page: int
    end_page: int
    start_offset: int
    end_offset: int
    content_sha256: str
    chunker_version: str

    def __post_init__(self) -> None:
        if self.chunk_index < 0:
            raise ValueError("Chunk index must not be negative.")
        if self.start_page < 1 or self.end_page < self.start_page:
            raise ValueError("Chunk page range is invalid.")
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise ValueError("Chunk offsets are invalid.")
        if len(self.content_sha256) != 64:
            raise ValueError("Chunk SHA-256 must contain 64 characters.")
        if not self.chunker_version.strip():
            raise ValueError("Chunker version must not be empty.")
