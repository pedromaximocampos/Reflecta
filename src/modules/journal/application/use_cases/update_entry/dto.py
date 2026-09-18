from dataclasses import dataclass, field

from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.value_objects.content_tags import ContentTags
from src.modules.journal.public.journal_entry_id import JournalEntryId


@dataclass(frozen=True, slots=True)
class UpdateJournalEntryInputDTO:
    journal_entry_id: JournalEntryId
    user_id: UserId
    title: str | None = None
    content_text: str | None = None
    context_tags: ContentTags | None = None
    fields_to_update: frozenset[str] = field(default_factory=frozenset)
