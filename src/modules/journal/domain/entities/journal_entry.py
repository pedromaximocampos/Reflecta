from dataclasses import dataclass
from datetime import datetime

from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.exceptions.journal_exceptions import (
    EmptyJournalContentError,
    JournalEntryNotEditableError,
)
from src.modules.journal.domain.value_objects.content_tags import ContentTags
from src.modules.journal.domain.value_objects.journal_entry_status import (
    JournalEntryStatus,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId


@dataclass(eq=False, slots=True)
class JournalEntry:
    id: JournalEntryId
    user_id: UserId
    title: str | None
    content_text: str
    status: JournalEntryStatus
    created_at: datetime
    context_tags: ContentTags | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        self.content_text = self._validate_content(self.content_text)
        self.title = self._normalize_title(self.title)

    @property
    def is_draft(self) -> bool:
        return self.status is JournalEntryStatus.DRAFT

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None or self.status is JournalEntryStatus.DELETED

    def update_title(self, title: str | None, *, now: datetime) -> None:
        self._ensure_editable()
        self.title = self._normalize_title(title)
        self.updated_at = now

    def update_content(self, content_text: str, *, now: datetime) -> None:
        self._ensure_editable()
        self.content_text = self._validate_content(content_text)
        self.updated_at = now

    def update_context_tags(
        self,
        context_tags: ContentTags | None,
        *,
        now: datetime,
    ) -> None:
        self._ensure_editable()
        self.context_tags = context_tags
        self.updated_at = now

    def mark_pending_analysis(self, *, now: datetime) -> None:
        self._ensure_editable()
        self.status = JournalEntryStatus.PENDING_ANALYSIS
        self.updated_at = now

    def mark_analyzed(self, *, now: datetime) -> None:
        if self.status is not JournalEntryStatus.PENDING_ANALYSIS:
            raise JournalEntryNotEditableError()
        self.status = JournalEntryStatus.ANALYZED
        self.updated_at = now

    def mark_analysis_failed(self, *, now: datetime) -> None:
        if self.status is not JournalEntryStatus.PENDING_ANALYSIS:
            raise JournalEntryNotEditableError()
        self.status = JournalEntryStatus.ANALYSIS_FAILED
        self.updated_at = now

    def delete(self, *, now: datetime) -> None:
        if self.is_deleted:
            return
        self.status = JournalEntryStatus.DELETED
        self.deleted_at = now
        self.updated_at = now

    @staticmethod
    def _validate_content(content_text: str) -> str:
        normalized = content_text.strip()
        if not normalized:
            raise EmptyJournalContentError()
        return normalized

    @staticmethod
    def _normalize_title(title: str | None) -> str | None:
        if title is None:
            return None
        normalized = title.strip()
        return normalized or None

    def _ensure_editable(self) -> None:
        if not self.is_draft or self.is_deleted:
            raise JournalEntryNotEditableError()
