from dataclasses import dataclass
from datetime import datetime

from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.domain.value_objects.content_tags import ContentTags
from src.modules.journal.domain.value_objects.journal_entry_status import (
    JournalEntryStatus,
)
from src.modules.journal.public.journal_entry_id import JournalEntryId


@dataclass(frozen=True, slots=True)
class JournalEntryOutputDTO:
    id: JournalEntryId
    user_id: UserId
    title: str | None
    content_text: str
    context_tags: ContentTags | None
    status: JournalEntryStatus
    created_at: datetime
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, journal_entry: JournalEntry) -> "JournalEntryOutputDTO":
        return cls(
            id=journal_entry.id,
            user_id=journal_entry.user_id,
            title=journal_entry.title,
            content_text=journal_entry.content_text,
            context_tags=journal_entry.context_tags,
            status=journal_entry.status,
            created_at=journal_entry.created_at,
            updated_at=journal_entry.updated_at,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id.value,
            "user_id": self.user_id.value,
            "title": self.title,
            "content_text": self.content_text,
            "context_tags": self.context_tags,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass(frozen=True, slots=True)
class JournalEntriesOutputDTO:
    entries: list[JournalEntryOutputDTO]

    @classmethod
    def from_entities(
        cls,
        journal_entries: list[JournalEntry],
    ) -> "JournalEntriesOutputDTO":
        return cls(
            entries=[
                JournalEntryOutputDTO.from_entity(entry) for entry in journal_entries
            ]
        )

    def to_dict(self) -> dict:
        return {"entries": [entry.to_dict() for entry in self.entries]}
