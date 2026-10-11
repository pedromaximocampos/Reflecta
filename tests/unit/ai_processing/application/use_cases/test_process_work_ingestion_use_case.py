from copy import deepcopy
from datetime import UTC, datetime

import pytest

from src.modules.ai_processing.application.dto import (
    ExtractedDocumentDTO,
    ExtractedPageDTO,
    StorageObjectLocationDTO,
    StoredNormalizedTextDTO,
    SuggestedPassageDTO,
    SuggestedPassageThemeDTO,
    WorkChunkAnalysisDTO,
)
from src.modules.ai_processing.application.exceptions import (
    WorkIngestionProcessingError,
    WorkPassageAnalysisError,
)
from src.modules.ai_processing.application.use_cases.process_work_ingestion import (
    ProcessWorkIngestionInputDTO,
    ProcessWorkIngestionUseCase,
)
from src.modules.ai_processing.domain.entities import WorkIngestionChunk
from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.modules.ai_processing.infrastructure.document import (
    BoundaryAwareTextChunker,
    UnicodeTextNormalizer,
)
from src.modules.ai_processing.public import WorkIngestionChunkId
from src.modules.auth.public import UserId
from src.modules.catalog.public.analysis_theme import ThemeOption
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId

NOW = datetime(2026, 10, 8, 12, 0, tzinfo=UTC)
INGESTION_ID = WorkIngestionId("01KTESTINGESTION000000000")


class _Clock:
    def now(self) -> datetime:
        return NOW


class _Ids:
    def __init__(self) -> None:
        self.value = 0

    def generate_ulid(self) -> str:
        self.value += 1
        return f"01KTESTCHUNK{self.value:014d}"


class _ChunkRepository:
    def __init__(self, chunks: tuple[WorkIngestionChunk, ...]) -> None:
        self.chunks = {chunk.id.value: deepcopy(chunk) for chunk in chunks}

    async def create_many(self, chunks):
        for chunk in chunks:
            self.chunks.setdefault(chunk.id.value, deepcopy(chunk))
        return tuple(deepcopy(chunk) for chunk in self.chunks.values())

    async def find_by_id(self, chunk_id):
        chunk = self.chunks.get(chunk_id.value)
        return deepcopy(chunk) if chunk else None

    async def list_by_ingestion(self, ingestion_id, *, statuses=None):
        chunks = [
            deepcopy(chunk)
            for chunk in self.chunks.values()
            if chunk.ingestion_id == ingestion_id
            and (statuses is None or chunk.status in statuses)
        ]
        return tuple(sorted(chunks, key=lambda item: item.chunk_index))

    async def claim_next(self, ingestion_id, *, now, lease_expires_at):
        for stored in sorted(self.chunks.values(), key=lambda item: item.chunk_index):
            reclaimable = (
                stored.status is WorkIngestionChunkStatus.PROCESSING
                and stored.lease_expires_at is not None
                and stored.lease_expires_at <= now
            )
            if stored.ingestion_id != ingestion_id or not (
                stored.status
                in {WorkIngestionChunkStatus.PENDING, WorkIngestionChunkStatus.FAILED}
                or reclaimable
            ):
                continue
            claimed = deepcopy(stored)
            claimed.mark_processing(now=now, lease_expires_at=lease_expires_at)
            self.chunks[claimed.id.value] = deepcopy(claimed)
            return claimed
        return None

    async def update(self, chunk):
        self.chunks[chunk.id.value] = deepcopy(chunk)
        return deepcopy(chunk)

    async def update_claimed(self, chunk, *, expected_attempts):
        stored = self.chunks.get(chunk.id.value)
        if (
            stored is None
            or stored.status is not WorkIngestionChunkStatus.PROCESSING
            or stored.attempts != expected_attempts
        ):
            return None
        self.chunks[chunk.id.value] = deepcopy(chunk)
        return deepcopy(chunk)

    async def count_by_status(self, ingestion_id):
        counts = {}
        for chunk in self.chunks.values():
            if chunk.ingestion_id == ingestion_id:
                counts[chunk.status] = counts.get(chunk.status, 0) + 1
        return counts


class _Uow:
    def __init__(self, repository: _ChunkRepository) -> None:
        self.work_ingestion_chunk_repository = repository

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        return None

    async def rollback(self):
        return None


class _Storage:
    def __init__(self, text: str) -> None:
        self.text = text
        self.saved_key: str | None = None

    async def download_document(self, *, location, destination):
        destination.write(b"fake-pdf")
        destination.seek(0)

    async def save_normalized_text(self, *, object_key, text, normalizer_version):
        import hashlib

        self.text = text
        self.saved_key = object_key
        content = text.encode("utf-8")
        return StoredNormalizedTextDTO(
            location=StorageObjectLocationDTO("reflecta-test", object_key),
            content_sha256=hashlib.sha256(content).hexdigest(),
            size_bytes=len(content),
        )

    async def load_normalized_text(self, **kwargs):
        return self.text


class _Themes:
    def __init__(self) -> None:
        self.themes = (
            ThemeOption(
                id="theme-1",
                slug="virtude",
                label="Virtude",
                description="Ação ética e caráter.",
            ),
        )

    async def active_themes(self):
        return self.themes


class _Analyzer:
    def __init__(
        self,
        *,
        fail: bool = False,
        error: Exception | None = None,
    ) -> None:
        self.fail = fail
        self.error = error
        self.received: list[str] = []

    async def analyze(self, *, work_id, chunk_text, themes):
        self.received.append(chunk_text)
        if self.error is not None:
            raise self.error
        if self.fail:
            raise RuntimeError("provider unavailable")
        quote = chunk_text[:25]
        return WorkChunkAnalysisDTO(
            passages=(
                SuggestedPassageDTO(
                    exact_text=quote,
                    chunk_start_offset=0,
                    chunk_end_offset=len(quote),
                    paraphrase="Síntese da passagem.",
                    rationale="A passagem se relaciona à virtude.",
                    themes=(SuggestedPassageThemeDTO("theme-1", 0.9),),
                ),
            )
        )


class _Passages:
    def __init__(self) -> None:
        self.calls = []

    async def replace_chunk_suggestions(self, **kwargs):
        self.calls.append(kwargs)


class _Ingestions:
    def __init__(self) -> None:
        self.pending_review = False
        self.failed = False
        self.error_code: str | None = None

    async def mark_processing(self, ingestion_id, *, now):
        return True

    async def mark_pending_review(self, ingestion_id, *, now):
        self.pending_review = True

    async def mark_failed(self, ingestion_id, *, now, error_code, error_message):
        self.failed = True
        self.error_code = error_code


class _UnusedDocumentComponent:
    def __getattr__(self, name):
        raise AssertionError(
            f"Document component should not be used during resume: {name}"
        )


class _Extractor:
    def __init__(self, text: str) -> None:
        self.text = text

    async def extract(self, document):
        return ExtractedDocumentDTO((ExtractedPageDTO(1, self.text),))


def _chunk(
    chunk_id: str,
    index: int,
    start: int,
    end: int,
    text: str,
    status: WorkIngestionChunkStatus,
) -> WorkIngestionChunk:
    import hashlib

    return WorkIngestionChunk(
        id=WorkIngestionChunkId(chunk_id),
        ingestion_id=INGESTION_ID,
        chunk_index=index,
        start_page=index + 1,
        end_page=index + 1,
        start_offset=start,
        end_offset=end,
        content_sha256=hashlib.sha256(text[start:end].encode("utf-8")).hexdigest(),
        chunker_version="test-v1",
        created_at=NOW,
        updated_at=NOW,
        status=status,
        attempts=1 if status is WorkIngestionChunkStatus.COMPLETED else 0,
        started_at=NOW if status is WorkIngestionChunkStatus.COMPLETED else None,
        finished_at=NOW if status is WorkIngestionChunkStatus.COMPLETED else None,
    )


def _input() -> ProcessWorkIngestionInputDTO:
    return ProcessWorkIngestionInputDTO(
        event_id="event-1",
        ingestion_id=INGESTION_ID,
        work_id=WorkId("01KTESTWORK00000000000000"),
        requested_by=UserId("01KTESTUSER00000000000000"),
        source_document=StorageObjectLocationDTO(
            bucket="reflecta-test",
            object_key="works/source.pdf",
        ),
        occurred_at=NOW,
    )


def _use_case(
    repository,
    analyzer,
    passages,
    ingestions,
    text,
    *,
    extractor=None,
    normalizer=None,
    chunker=None,
    storage=None,
):
    unused = _UnusedDocumentComponent()
    return ProcessWorkIngestionUseCase(
        ai_processing_uow=_Uow(repository),
        work_ingestion_storage=storage or _Storage(text),
        document_text_extractor=extractor or unused,
        text_normalizer=normalizer or unused,
        text_chunker=chunker or unused,
        theme_catalog=_Themes(),
        passage_analyzer=analyzer,
        passage_candidate_catalog=passages,
        work_ingestion_catalog=ingestions,
        ulid_generator=_Ids(),
        clock=_Clock(),
    )


@pytest.mark.asyncio
async def test_first_execution_normalizes_persists_and_processes_all_chunks() -> None:
    source_text = " ".join(
        f"Palavra{index}." if index % 7 == 0 else f"palavra{index}"
        for index in range(45)
    )
    repository = _ChunkRepository(())
    storage = _Storage("")
    analyzer = _Analyzer()
    passages = _Passages()
    ingestions = _Ingestions()

    result = await _use_case(
        repository,
        analyzer,
        passages,
        ingestions,
        "",
        extractor=_Extractor(source_text),
        normalizer=UnicodeTextNormalizer(),
        chunker=BoundaryAwareTextChunker(
            min_tokens=8,
            max_tokens=14,
            overlap_tokens=3,
        ),
        storage=storage,
    ).execute(_input())

    assert result.total_chunks >= 2
    assert result.completed_chunks == result.total_chunks
    assert len(analyzer.received) == result.total_chunks
    assert len(passages.calls) == result.total_chunks
    assert storage.saved_key == (
        "works/01KTESTWORK00000000000000/processing/"
        "01KTESTINGESTION000000000/normalized.txt"
    )
    assert ingestions.pending_review is True


@pytest.mark.asyncio
async def test_resume_processes_only_incomplete_chunks_and_finishes_ingestion() -> None:
    text = "Trecho já concluído. Trecho pendente muito relevante para esta análise."
    split = text.index("Trecho pendente")
    repository = _ChunkRepository(
        (
            _chunk(
                "chunk-1", 0, 0, split - 1, text, WorkIngestionChunkStatus.COMPLETED
            ),
            _chunk(
                "chunk-2", 1, split, len(text), text, WorkIngestionChunkStatus.PENDING
            ),
        )
    )
    analyzer = _Analyzer()
    passages = _Passages()
    ingestions = _Ingestions()

    result = await _use_case(repository, analyzer, passages, ingestions, text).execute(
        _input()
    )

    assert result.total_chunks == 2
    assert result.completed_chunks == 2
    assert analyzer.received == [text[split:]]
    assert len(passages.calls) == 1
    assert ingestions.pending_review is True
    assert ingestions.failed is False


@pytest.mark.asyncio
async def test_failure_marks_claimed_chunk_and_ingestion_failed_for_sqs_retry() -> None:
    text = "Trecho pendente com conteúdo suficiente para realizar a análise."
    repository = _ChunkRepository(
        (_chunk("chunk-1", 0, 0, len(text), text, WorkIngestionChunkStatus.PENDING),)
    )
    analyzer = _Analyzer(fail=True)
    ingestions = _Ingestions()

    with pytest.raises(WorkIngestionProcessingError):
        await _use_case(repository, analyzer, _Passages(), ingestions, text).execute(
            _input()
        )

    stored = repository.chunks["chunk-1"]
    assert stored.status is WorkIngestionChunkStatus.FAILED
    assert stored.attempts == 1
    assert ingestions.failed is True
    assert ingestions.pending_review is False


@pytest.mark.asyncio
async def test_failure_persists_sanitized_analysis_error_code() -> None:
    text = "Trecho pendente com conteúdo suficiente para realizar a análise."
    repository = _ChunkRepository(
        (_chunk("chunk-1", 0, 0, len(text), text, WorkIngestionChunkStatus.PENDING),)
    )
    analyzer = _Analyzer(
        error=WorkPassageAnalysisError(
            "Work passage analysis failed.",
            code="quote_not_found",
        )
    )
    ingestions = _Ingestions()

    with pytest.raises(WorkPassageAnalysisError):
        await _use_case(repository, analyzer, _Passages(), ingestions, text).execute(
            _input()
        )

    assert repository.chunks["chunk-1"].error_code == "quote_not_found"
    assert ingestions.error_code == "quote_not_found"
