from dataclasses import dataclass
from datetime import datetime

from src.modules.catalog.domain.exceptions.passage_exceptions import (
    InvalidPassageTransitionError,
)
from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.theme_id import ThemeId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(frozen=True, slots=True)
class PassageThemeRelevance:
    theme_id: ThemeId
    confidence: float

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("Passage theme confidence must be between 0 and 1.")


@dataclass(eq=False, slots=True)
class Passage:
    id: PassageId
    work_id: WorkId
    source_key: str
    locator: str
    short_text: str
    paraphrase: str
    interpretation_note: str
    status: CatalogStatus
    priority: int
    themes: tuple[PassageThemeRelevance, ...]
    created_at: datetime
    ingestion_id: WorkIngestionId | None = None
    source_chunk_id: str | None = None
    source: str = "ai"
    start_page: int | None = None
    end_page: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.source_key.strip() or len(self.source_key) != 64:
            raise ValueError("Passage source key must be a SHA-256 hash.")
        if self.source not in {"ai", "admin"}:
            raise ValueError("Passage source must be 'ai' or 'admin'.")
        if self.source == "ai" and (
            self.ingestion_id is None
            or self.source_chunk_id is None
            or not self.source_chunk_id.strip()
        ):
            raise ValueError("AI passages require ingestion and chunk identifiers.")
        if not self.locator.strip() or not self.short_text.strip():
            raise ValueError("Passage locator and text must not be empty.")
        if not self.paraphrase.strip() or not self.interpretation_note.strip():
            raise ValueError("Passage interpretation fields must not be empty.")
        if self.priority < 0:
            raise ValueError("Passage priority must not be negative.")
        if (self.start_page is None) != (self.end_page is None):
            raise ValueError("Passage page range must be complete.")
        if self.start_page is not None and (
            self.start_page < 1 or self.end_page < self.start_page
        ):
            raise ValueError("Passage page range is invalid.")
        if (self.start_offset is None) != (self.end_offset is None):
            raise ValueError("Passage offsets must be complete.")
        if self.start_offset is not None and (
            self.start_offset < 0 or self.end_offset <= self.start_offset
        ):
            raise ValueError("Passage offsets are invalid.")
        theme_ids = tuple(theme.theme_id.value for theme in self.themes)
        if not theme_ids or len(theme_ids) != len(set(theme_ids)):
            raise ValueError("Passage themes must be non-empty and unique.")

    def update(
        self,
        *,
        now: datetime,
        locator: str | None = None,
        short_text: str | None = None,
        paraphrase: str | None = None,
        interpretation_note: str | None = None,
        priority: int | None = None,
        themes: tuple[PassageThemeRelevance, ...] | None = None,
        start_page: int | None = None,
        end_page: int | None = None,
        update_page_range: bool = False,
    ) -> None:
        self.locator = self.locator if locator is None else locator
        self.short_text = self.short_text if short_text is None else short_text
        self.paraphrase = self.paraphrase if paraphrase is None else paraphrase
        self.interpretation_note = (
            self.interpretation_note
            if interpretation_note is None
            else interpretation_note
        )
        self.priority = self.priority if priority is None else priority
        self.themes = self.themes if themes is None else themes
        if update_page_range:
            self.start_page = start_page
            self.end_page = end_page
        self.updated_at = now
        self.__post_init__()

    def approve(self, *, now: datetime) -> None:
        self._transition(
            CatalogStatus.APPROVED,
            allowed_from={CatalogStatus.PENDING_REVIEW},
            now=now,
        )

    def reject(self, *, now: datetime) -> None:
        self._transition(
            CatalogStatus.REJECTED,
            allowed_from={CatalogStatus.PENDING_REVIEW},
            now=now,
        )

    def activate(self, *, now: datetime) -> None:
        self._transition(
            CatalogStatus.ACTIVE,
            allowed_from={CatalogStatus.APPROVED, CatalogStatus.INACTIVE},
            now=now,
        )

    def deactivate(self, *, now: datetime) -> None:
        self._transition(
            CatalogStatus.INACTIVE,
            allowed_from={CatalogStatus.APPROVED, CatalogStatus.ACTIVE},
            now=now,
        )

    def retire(self, *, now: datetime) -> None:
        if self.status is CatalogStatus.PENDING_REVIEW:
            self.reject(now=now)
        elif self.status in {CatalogStatus.APPROVED, CatalogStatus.ACTIVE}:
            self.deactivate(now=now)
        elif self.status not in {CatalogStatus.REJECTED, CatalogStatus.INACTIVE}:
            raise InvalidPassageTransitionError(
                self.status.value,
                CatalogStatus.INACTIVE.value,
            )

    def _transition(
        self,
        target: CatalogStatus,
        *,
        allowed_from: set[CatalogStatus],
        now: datetime,
    ) -> None:
        if self.status is target:
            return
        if self.status not in allowed_from:
            raise InvalidPassageTransitionError(self.status.value, target.value)
        self.status = target
        self.updated_at = now
