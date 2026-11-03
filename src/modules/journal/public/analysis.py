from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


class AnalysisConflictError(Exception):
    """Entry changed, was deleted, or already has a completed analysis."""


class UserReprocessLimitError(Exception):
    """Only an administrator may request another attempt for this entry."""


USER_REPROCESS_LIMIT = 3


def reprocess_policy(entry):
    used = entry.user_reprocess_count or 0
    failed = entry.status == "analysis_failed"
    return {"user_limit": USER_REPROCESS_LIMIT, "user_used": used,
            "user_remaining": max(0, USER_REPROCESS_LIMIT - used),
            "can_user_reprocess": failed and used < USER_REPROCESS_LIMIT,
            "requires_admin": failed and used >= USER_REPROCESS_LIMIT,
            "revision": (entry.updated_at or entry.created_at).isoformat()}


@dataclass(frozen=True)
class AnalysisFailure:
    code: str
    message: str
    attempts: int


@dataclass(frozen=True)
class EntrySnapshot:
    entry_id: str
    user_id: str
    content_text: str
    context_tags: dict[str, Any] | None
    updated_at: datetime | None
    status: str
    processing_settings: dict[str, Any] | None = None


@dataclass(frozen=True)
class SentencePassageAnalysis:
    id: str
    passage_id: str
    confidence: float
    reason: str
    payload_snapshot: dict[str, Any]


@dataclass(frozen=True)
class SentenceAnalysis:
    id: str
    sentence_index: int
    sentence_text: str
    start_offset: int
    end_offset: int
    themes: tuple[dict[str, Any], ...]
    passages: tuple[SentencePassageAnalysis, ...] = ()


class IJournalAnalysisGateway(Protocol):
    async def read(self, entry_id: str, user_id: str) -> EntrySnapshot: ...

    async def save(
        self, snapshot: EntrySnapshot, *, analysis_id: str, summary: str,
        main_message: str, metadata: dict[str, Any], now: datetime,
        sentences: tuple[SentenceAnalysis, ...],
    ) -> None: ...
