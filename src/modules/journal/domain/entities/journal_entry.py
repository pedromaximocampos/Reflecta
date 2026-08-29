from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Mapping, Any

from src.domain.exceptions.domain_error import DomainError
from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.value_objects.content_tags import ContentTags
from src.modules.journal.domain.value_objects.journal_entry_status import JournalEntryStatus


@dataclass(eq=False, slots=True)
class JournalEntry:
    id: str
    user_id: UserId
    title: str
    content_text: str  # should be encrypted at the boundaries (application/infra)
    status: JournalEntryStatus
    created_at: datetime

    updated_at:  Optional[datetime] = None

    # Derived / AI-related fields (optional)
    content_meta: Optional[dict[str, Any]] = None   # analysis output (summary, themes, practices...)
    content_tags: Optional[ContentTags] = None    # tags with source/confidence/user approval, etc.

    analyzed_at: Optional[datetime] = None
    analysis_error: Optional[str] = None

    @property
    def is_draft(self) -> bool:
        return self.status == JournalEntryStatus.DRAFT

    @property
    def is_finalized(self) -> bool:
        return self.status != JournalEntryStatus.DRAFT

    @property
    def is_pending_analysis(self) -> bool:
        return self.status == JournalEntryStatus.PENDING_ANALYSIS

    @property
    def is_analyzed(self) -> bool:
        return self.status == JournalEntryStatus.ANALYZED and self.analyzed_at is not None

    @property
    def is_analysis_failed(self) -> bool:
        return self.status == JournalEntryStatus.ANALYSIS_FAILED


    def update_title(self, new_title: Optional[str], *, now: datetime) -> None:
        self._ensure_editable()
        self.title = new_title
        self.updated_at = now

    def update_content(self, new_content_text: str, *, now: datetime) -> None:
        self._ensure_editable()
        if not new_content_text or not new_content_text.strip():
            raise DomainError("content_text cannot be empty.")
        self.content_text = new_content_text
        self.updated_at = now

    def update_context_tags(self, tags: ContentTags, *, now: datetime) -> None:
        """
        Context tags can be set while draft (and optionally later if you allow).
        Keeping it draft-only reduces confusion and avoids retroactive rewriting.
        """
        self._ensure_editable()
        self.content_tags = tags if tags is not None else None
        self.updated_at = now

    def request_analysis(self, *, now: datetime) -> None:
        """
        User explicitly requests analysis.
        Locks entry for editing and moves to pending.
        """
        if self.status != JournalEntryStatus.DRAFT:
            raise DomainError("Only draft entries can be sent to analysis.")
        self.status = JournalEntryStatus.PENDING_ANALYSIS
        self.analysis_error = None
        self.updated_at = now

    def mark_analyzed(self, content_meta: Mapping[str, Any], *, now: datetime) -> None:
        """
        Worker marks analysis success.
        """
        if self.status != JournalEntryStatus.PENDING_ANALYSIS:
            raise DomainError("Entry is not pending analysis.")

        if not content_meta:
            raise DomainError("content_meta cannot be empty when marking analyzed.")
        self.status = JournalEntryStatus.ANALYZED
        self.analyzed_at = now
        self.analysis_error = None
        self.content_meta = dict(content_meta)
        self.updated_at = now

    def mark_analysis_failed(self, error: str, *, now: datetime) -> None:
        """
        Worker marks analysis failure.
        """
        if self.status != JournalEntryStatus.PENDING_ANALYSIS:
            raise DomainError("Entry is not pending analysis.")
        if not error.strip():
            raise DomainError("analysis_error cannot be empty.")
        self.status = JournalEntryStatus.ANALYSIS_FAILED
        self.analysis_error = error
        self.updated_at = now

    def retry_analysis(self, *, now: datetime) -> None:
        """
        Allows retry only when failed.
        """
        if self.status != JournalEntryStatus.ANALYSIS_FAILED:
            raise DomainError("Only failed analyses can be retried.")
        self.status = JournalEntryStatus.PENDING_ANALYSIS
        self.analysis_error = None
        self.updated_at = now

    def reopen_for_editing(self, *, now: datetime, clear_analysis: bool = True) -> None:
        """
        Optional: allow user to reopen an analyzed entry to edit.
        Default behavior clears analysis so the next analysis is not misleading.
        """
        if self.status not in {JournalEntryStatus.ANALYZED, JournalEntryStatus.ANALYSIS_FAILED}:
            raise DomainError("Only analyzed/failed entries can be reopened.")
        self.status = JournalEntryStatus.DRAFT
        if clear_analysis:
            self.content_meta = None
            self.analyzed_at = None
            self.analysis_error = None
            self.content_tags = None
        self.updated_at = now


    def set_ai_tags(self, tags: ContentTags, *, now: datetime) -> None:
        """
        If you want IA tags generation right after save (still draft) OR after analysis,
        you can permit both states here.
        """
        if self.status not in {JournalEntryStatus.DRAFT, JournalEntryStatus.ANALYZED}:
            raise DomainError("Cannot set AI tags in the current state.")
        self.content_tags = tags
        self.updated_at = now

    def __repr__(self) -> str:
        return (
            "JournalEntry("
            f"id={self.id}, user_id={self.user_id}, title={self.title!r}, status={self.status.value})"
        )


    def _ensure_editable(self) -> None:
        if self.status != JournalEntryStatus.DRAFT:
            raise DomainError("Entry is not editable unless it is in DRAFT status.")
