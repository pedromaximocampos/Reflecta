from dataclasses import dataclass
from datetime import date

from src.modules.auth.public.user_id import UserId
from src.modules.journal.application.dto.journal_entry import JournalEntryOutputDTO
from src.modules.journal.domain.value_objects.content_tags import ContentTags

@dataclass(frozen=True)
class CreateJournalEntryDTO:
    user_id: UserId
    title: str | None
    content_text: str
    entry_date: date | None = None
    context_tags: ContentTags | None = None


CreateJournalEntryOutputDTO = JournalEntryOutputDTO
