from dataclasses import dataclass

from src.domain.value_objects.user_id import UserId


@dataclass(frozen=True)
class CreateJournalEntryDTO:
    user_id: UserId
    title: str
    content_text: str