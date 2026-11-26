import hashlib
import logging
from datetime import datetime, timedelta
from tempfile import SpooledTemporaryFile

from src.modules.ai_processing.application.contracts import IThemeCatalog
from src.modules.ai_processing.application.dto import (
    StorageObjectLocationDTO,
    WorkChunkAnalysisDTO,
)
from src.modules.ai_processing.application.exceptions import (
    WorkDocumentChunkingError,
    WorkDocumentExtractionError,
    WorkDocumentNormalizationError,
    WorkIngestionConcurrentProcessingError,
    WorkIngestionProcessingError,
    WorkIngestionProcessingStorageError,
    WorkPassageAnalysisError,
)
from src.modules.ai_processing.application.ports.analysis import IWorkPassageAnalyzer
from src.modules.ai_processing.application.ports.catalog import (
    IPassageCandidateCatalog,
    IWorkIngestionCatalog,
)
from src.modules.ai_processing.application.ports.document import (
    ITextChunker,
    ITextNormalizer,
    IWorkDocumentTextExtractor,
)
from src.modules.ai_processing.application.ports.storage import IWorkIngestionStorage
from src.modules.ai_processing.domain.entities import (
    WorkIngestionChunk,
    WorkIngestionFailureAttempt,
)
from src.modules.ai_processing.domain.ports.unit_of_work import (
    IAIProcessingUnitOfWork,
)
from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.modules.ai_processing.public import WorkIngestionChunkId
from src.modules.catalog.public.analysis_theme import ThemeOption
from src.modules.catalog.public.passage_candidate import (
    PassageSuggestion,
    PassageThemeSuggestion,
)
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator

from .dto import ProcessWorkIngestionInputDTO, ProcessWorkIngestionOutputDTO
from .iprocess_work_ingestion_use_case import IProcessWorkIngestionUseCase

_LOGGER = logging.getLogger(__name__)


class ProcessWorkIngestionUseCase(IProcessWorkIngestionUseCase):
    """Orchestrates UC23 with durable, independently retryable chunk checkpoints."""

    _MAX_IN_MEMORY_PDF_BYTES = 64 * 1024 * 1024

    def __init__(
        self,
        ai_processing_uow: IAIProcessingUnitOfWork,
        work_ingestion_storage: IWorkIngestionStorage,
        document_text_extractor: IWorkDocumentTextExtractor,
        text_normalizer: ITextNormalizer,
        text_chunker: ITextChunker,
        theme_catalog: IThemeCatalog,
        passage_analyzer: IWorkPassageAnalyzer,
        passage_candidate_catalog: IPassageCandidateCatalog,
        work_ingestion_catalog: IWorkIngestionCatalog,
        ulid_generator: IULIDGenerator,
        clock: IClock,
        *,
        chunk_lease_seconds: int = 900,
    ) -> None:
        if chunk_lease_seconds <= 0:
            raise ValueError("Chunk lease duration must be positive.")
        self._ai_processing_uow = ai_processing_uow
        self._work_ingestion_storage = work_ingestion_storage
        self._document_text_extractor = document_text_extractor
        self._text_normalizer = text_normalizer
        self._text_chunker = text_chunker
        self._theme_catalog = theme_catalog
        self._passage_analyzer = passage_analyzer
        self._passage_candidate_catalog = passage_candidate_catalog
        self._work_ingestion_catalog = work_ingestion_catalog
        self._ulid_generator = ulid_generator
        self._clock = clock
        self._chunk_lease = timedelta(seconds=chunk_lease_seconds)

    async def execute(
        self,
        ingestion_input: ProcessWorkIngestionInputDTO,
    ) -> ProcessWorkIngestionOutputDTO:
        current_chunk: WorkIngestionChunk | None = None
        current_chunk_text: str | None = None
        _LOGGER.info(
            "Work ingestion started: event_id=%s ingestion_id=%s delivery_attempt=%s",
            ingestion_input.event_id,
            ingestion_input.ingestion_id.value,
            ingestion_input.delivery_attempt,
        )
        should_process = await self._work_ingestion_catalog.mark_processing(
            ingestion_input.ingestion_id,
            now=self._clock.now(),
        )
        if not should_process:
            counts = await self._chunk_counts(ingestion_input)
            total_chunks = sum(counts.values())
            return ProcessWorkIngestionOutputDTO(
                ingestion_id=ingestion_input.ingestion_id,
                total_chunks=total_chunks,
                completed_chunks=counts.get(
                    WorkIngestionChunkStatus.COMPLETED,
                    0,
                ),
            )
        try:
            normalized_text = await self._load_or_prepare_document(ingestion_input)
            themes = await self._theme_catalog.active_themes()
            if not themes:
                raise WorkIngestionProcessingError(
                    "No active themes are available for work analysis."
                )

            while True:
                current_chunk = await self._claim_next_chunk(ingestion_input)
                if current_chunk is None:
                    counts = await self._chunk_counts(ingestion_input)
                    total_chunks = sum(counts.values())
                    completed_chunks = counts.get(
                        WorkIngestionChunkStatus.COMPLETED,
                        0,
                    )
                    if total_chunks == 0:
                        raise WorkIngestionProcessingError(
                            "The work ingestion has no chunks."
                        )
                    if completed_chunks == total_chunks:
                        await self._work_ingestion_catalog.mark_pending_review(
                            ingestion_input.ingestion_id,
                            now=self._clock.now(),
                        )
                        output = ProcessWorkIngestionOutputDTO(
                            ingestion_id=ingestion_input.ingestion_id,
                            total_chunks=total_chunks,
                            completed_chunks=completed_chunks,
                        )
                        _LOGGER.info(
                            "Work ingestion pending review: ingestion_id=%s total_chunks=%s",
                            ingestion_input.ingestion_id.value,
                            total_chunks,
                        )
                        return output
                    if counts.get(WorkIngestionChunkStatus.PROCESSING, 0):
                        raise WorkIngestionConcurrentProcessingError(
                            "Another worker owns an active chunk lease."
                        )
                    raise WorkIngestionProcessingError(
                        "The work ingestion has unfinished chunks that could not be claimed."
                    )

                chunk_text = self._slice_and_verify_chunk(
                    normalized_text,
                    current_chunk,
                )
                current_chunk_text = chunk_text
                analysis = await self._passage_analyzer.analyze(
                    work_id=ingestion_input.work_id,
                    chunk_text=chunk_text,
                    themes=themes,
                )
                await self._ensure_selected_themes_are_current(analysis, themes)
                suggestions = self._to_catalog_suggestions(current_chunk, analysis)
                await self._passage_candidate_catalog.replace_chunk_suggestions(
                    ingestion_id=ingestion_input.ingestion_id,
                    work_id=ingestion_input.work_id,
                    chunk_id=current_chunk.id.value,
                    suggestions=suggestions,
                )
                await self._mark_chunk_completed(current_chunk)
                current_chunk = None
                current_chunk_text = None
        except WorkIngestionConcurrentProcessingError:
            raise
        except Exception as error:
            if current_chunk is not None:
                await self._mark_chunk_failed(
                    ingestion_input,
                    current_chunk,
                    error,
                    context_text=current_chunk_text,
                )
            else:
                await self._record_ingestion_failure(ingestion_input, error)
            await self._mark_ingestion_failed(ingestion_input, error)
            if isinstance(error, WorkIngestionProcessingError):
                raise
            raise WorkIngestionProcessingError(
                "Work ingestion processing failed."
            ) from error

    async def _load_or_prepare_document(
        self,
        ingestion_input: ProcessWorkIngestionInputDTO,
    ) -> str:
        chunks = await self._list_chunks(ingestion_input)
        normalized_location = self._normalized_text_location(ingestion_input)
        if chunks:
            return await self._work_ingestion_storage.load_normalized_text(
                location=normalized_location,
            )

        with SpooledTemporaryFile(
            max_size=self._MAX_IN_MEMORY_PDF_BYTES,
            mode="w+b",
        ) as document:
            await self._work_ingestion_storage.download_document(
                location=ingestion_input.source_document,
                destination=document,
            )
            extracted = await self._document_text_extractor.extract(document)

        normalized = self._text_normalizer.normalize(extracted)
        stored = await self._work_ingestion_storage.save_normalized_text(
            object_key=normalized_location.object_key,
            text=normalized.text,
            normalizer_version=normalized.normalizer_version,
        )
        if stored.content_sha256 != normalized.content_sha256:
            raise WorkIngestionProcessingError(
                "The stored normalized text checksum is inconsistent."
            )
        drafts = self._text_chunker.create_chunks(normalized)
        if not drafts:
            raise WorkIngestionProcessingError(
                "The normalized document did not produce any chunks."
            )
        now = self._clock.now()
        entities = tuple(
            WorkIngestionChunk(
                id=WorkIngestionChunkId(self._ulid_generator.generate_ulid()),
                ingestion_id=ingestion_input.ingestion_id,
                chunk_index=draft.chunk_index,
                start_page=draft.start_page,
                end_page=draft.end_page,
                start_offset=draft.start_offset,
                end_offset=draft.end_offset,
                content_sha256=draft.content_sha256,
                chunker_version=draft.chunker_version,
                created_at=now,
                updated_at=now,
            )
            for draft in drafts
        )
        async with self._ai_processing_uow as uow:
            stored_chunks = await uow.work_ingestion_chunk_repository.create_many(
                entities
            )
            await uow.commit()
        _LOGGER.info(
            "Work ingestion document prepared: ingestion_id=%s chunks=%s",
            ingestion_input.ingestion_id.value,
            len(stored_chunks),
        )
        return normalized.text

    async def _list_chunks(
        self,
        ingestion_input: ProcessWorkIngestionInputDTO,
    ) -> tuple[WorkIngestionChunk, ...]:
        async with self._ai_processing_uow as uow:
            return await uow.work_ingestion_chunk_repository.list_by_ingestion(
                ingestion_input.ingestion_id
            )

    async def _claim_next_chunk(
        self,
        ingestion_input: ProcessWorkIngestionInputDTO,
    ) -> WorkIngestionChunk | None:
        now = self._clock.now()
        async with self._ai_processing_uow as uow:
            chunk = await uow.work_ingestion_chunk_repository.claim_next(
                ingestion_input.ingestion_id,
                now=now,
                lease_expires_at=now + self._chunk_lease,
            )
            await uow.commit()
            if chunk is not None:
                _LOGGER.info(
                    "Work ingestion chunk claimed: ingestion_id=%s chunk_id=%s "
                    "chunk_index=%s attempt=%s",
                    ingestion_input.ingestion_id.value,
                    chunk.id.value,
                    chunk.chunk_index,
                    chunk.attempts,
                )
            return chunk

    async def _mark_chunk_completed(self, chunk: WorkIngestionChunk) -> None:
        now = self._clock.now()
        expected_attempts = chunk.attempts
        chunk.mark_completed(now=now)
        async with self._ai_processing_uow as uow:
            updated = await uow.work_ingestion_chunk_repository.update_claimed(
                chunk,
                expected_attempts=expected_attempts,
            )
            if updated is None:
                raise WorkIngestionConcurrentProcessingError(
                    "The chunk lease was reclaimed by another worker."
                )
            await uow.commit()
        _LOGGER.info(
            "Work ingestion chunk completed: chunk_id=%s chunk_index=%s",
            chunk.id.value,
            chunk.chunk_index,
        )

    async def _mark_chunk_failed(
        self,
        ingestion_input: ProcessWorkIngestionInputDTO,
        chunk: WorkIngestionChunk,
        error: Exception,
        *,
        context_text: str | None,
    ) -> None:
        try:
            now = self._clock.now()
            expected_attempts = chunk.attempts
            chunk.mark_failed(
                now=now,
                error_code=_failure_code(error),
                error_message="Chunk processing failed; inspect worker logs.",
            )
            async with self._ai_processing_uow as uow:
                await uow.work_ingestion_chunk_repository.update_claimed(
                    chunk,
                    expected_attempts=expected_attempts,
                )
                failure = self._failure_attempt(
                    ingestion_input,
                    error,
                    attempt=chunk.attempts,
                    chunk=chunk,
                    occurred_at=now,
                    context_text=context_text,
                )
                await uow.work_ingestion_failure_repository.create(failure)
                await uow.commit()
            _LOGGER.error(
                "Work ingestion chunk failure recorded: failure_id=%s "
                "ingestion_id=%s chunk_id=%s attempt=%s error_code=%s",
                failure.id,
                ingestion_input.ingestion_id.value,
                chunk.id.value,
                chunk.attempts,
                failure.error_code,
            )
        except Exception:
            _LOGGER.exception(
                "Failed to persist chunk failure: chunk_id=%s",
                chunk.id.value,
            )

    async def _record_ingestion_failure(
        self,
        ingestion_input: ProcessWorkIngestionInputDTO,
        error: Exception,
    ) -> None:
        try:
            failure = self._failure_attempt(
                ingestion_input,
                error,
                attempt=max(1, ingestion_input.delivery_attempt),
                chunk=None,
                occurred_at=self._clock.now(),
            )
            async with self._ai_processing_uow as uow:
                await uow.work_ingestion_failure_repository.create(failure)
                await uow.commit()
            _LOGGER.error(
                "Work ingestion failure recorded: failure_id=%s "
                "ingestion_id=%s attempt=%s error_code=%s",
                failure.id,
                ingestion_input.ingestion_id.value,
                failure.attempt,
                failure.error_code,
            )
        except Exception:
            _LOGGER.exception(
                "Failed to persist ingestion failure context: ingestion_id=%s",
                ingestion_input.ingestion_id.value,
            )

    async def _mark_ingestion_failed(
        self,
        ingestion_input: ProcessWorkIngestionInputDTO,
        error: Exception,
    ) -> None:
        try:
            await self._work_ingestion_catalog.mark_failed(
                ingestion_input.ingestion_id,
                now=self._clock.now(),
                error_code=_failure_code(error),
                error_message="Work ingestion failed; inspect worker logs.",
            )
        except Exception:
            _LOGGER.exception(
                "Failed to persist ingestion failure: ingestion_id=%s",
                ingestion_input.ingestion_id.value,
            )

    def _failure_attempt(
        self,
        ingestion_input: ProcessWorkIngestionInputDTO,
        error: Exception,
        *,
        attempt: int,
        chunk: WorkIngestionChunk | None,
        occurred_at: datetime,
        context_text: str | None = None,
    ) -> WorkIngestionFailureAttempt:
        return WorkIngestionFailureAttempt(
            id=self._ulid_generator.generate_ulid(),
            ingestion_id=ingestion_input.ingestion_id,
            chunk_id=chunk.id if chunk else None,
            stage=_failure_stage(error),
            attempt=attempt,
            error_code=_failure_code(error),
            error_message=_failure_message(error),
            occurred_at=occurred_at,
            start_page=chunk.start_page if chunk else None,
            end_page=chunk.end_page if chunk else None,
            start_offset=chunk.start_offset if chunk else None,
            end_offset=chunk.end_offset if chunk else None,
            content_sha256=chunk.content_sha256 if chunk else None,
            provider_request_id=getattr(error, "request_id", None),
            provider_response_id=getattr(error, "response_id", None),
            context_text=context_text,
        )

    async def _chunk_counts(
        self,
        ingestion_input: ProcessWorkIngestionInputDTO,
    ) -> dict[WorkIngestionChunkStatus, int]:
        async with self._ai_processing_uow as uow:
            return await uow.work_ingestion_chunk_repository.count_by_status(
                ingestion_input.ingestion_id
            )

    async def _ensure_selected_themes_are_current(
        self,
        analysis: WorkChunkAnalysisDTO,
        snapshot: tuple[ThemeOption, ...],
    ) -> None:
        selected_ids = {
            theme.theme_id for passage in analysis.passages for theme in passage.themes
        }
        if not selected_ids:
            return
        snapshot_by_id = {theme.id: theme for theme in snapshot}
        current_by_id = {
            theme.id: theme for theme in await self._theme_catalog.active_themes()
        }
        if any(
            current_by_id.get(theme_id) != snapshot_by_id.get(theme_id)
            for theme_id in selected_ids
        ):
            raise WorkIngestionProcessingError(
                "Selected catalog themes changed during chunk analysis."
            )

    @staticmethod
    def _slice_and_verify_chunk(
        normalized_text: str,
        chunk: WorkIngestionChunk,
    ) -> str:
        if chunk.end_offset > len(normalized_text):
            raise WorkIngestionProcessingError(
                "Chunk offsets exceed the normalized text."
            )
        text = normalized_text[chunk.start_offset : chunk.end_offset]
        actual_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        if actual_hash != chunk.content_sha256:
            raise WorkIngestionProcessingError("Chunk checksum validation failed.")
        return text

    @staticmethod
    def _to_catalog_suggestions(
        chunk: WorkIngestionChunk,
        analysis: WorkChunkAnalysisDTO,
    ) -> tuple[PassageSuggestion, ...]:
        return tuple(
            PassageSuggestion(
                exact_text=passage.exact_text,
                paraphrase=passage.paraphrase,
                interpretation_note=passage.rationale,
                reflective_value=passage.reflective_value,
                reflective_note=passage.reflective_note,
                start_page=chunk.start_page,
                end_page=chunk.end_page,
                start_offset=chunk.start_offset + passage.chunk_start_offset,
                end_offset=chunk.start_offset + passage.chunk_end_offset,
                themes=tuple(
                    PassageThemeSuggestion(
                        theme_id=theme.theme_id,
                        confidence=theme.confidence,
                    )
                    for theme in passage.themes
                ),
            )
            for passage in analysis.passages
        )

    @staticmethod
    def _normalized_text_location(
        ingestion_input: ProcessWorkIngestionInputDTO,
    ) -> StorageObjectLocationDTO:
        return StorageObjectLocationDTO(
            bucket=ingestion_input.source_document.bucket,
            object_key=(
                f"works/{ingestion_input.work_id.value}/processing/"
                f"{ingestion_input.ingestion_id.value}/normalized.txt"
            ),
        )


def _failure_code(error: Exception) -> str:
    code = getattr(error, "code", None)
    if isinstance(code, str) and code.strip():
        return code.strip()[:128]
    return type(error).__name__[:128]


def _failure_message(error: Exception) -> str:
    message = " ".join(str(error).split())
    return (message or type(error).__name__)[:2000]


def _failure_stage(error: Exception) -> str:
    if isinstance(error, WorkIngestionProcessingStorageError):
        return "storage"
    if isinstance(error, WorkDocumentExtractionError):
        return "document_extraction"
    if isinstance(error, WorkDocumentNormalizationError):
        return "document_normalization"
    if isinstance(error, WorkDocumentChunkingError):
        return "document_chunking"
    if isinstance(error, WorkPassageAnalysisError):
        return "passage_analysis"
    return "work_ingestion"
