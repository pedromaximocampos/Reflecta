from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


class AnalysisConflictError(Exception):
    """Entry changed, was deleted, or already has a completed analysis."""


@dataclass(frozen=True)
class EntrySnapshot:
    entry_id: str
    user_id: str
    content_text: str
    context_tags: dict[str, Any] | None
    updated_at: datetime | None
    status: str


class IJournalAnalysisGateway(Protocol):
    async def read(self, entry_id: str, user_id: str) -> EntrySnapshot: ...

    async def save(
        self, snapshot: EntrySnapshot, *, analysis_id: str, summary: str,
        main_message: str, metadata: dict[str, Any], now: datetime,
    ) -> None: ...
