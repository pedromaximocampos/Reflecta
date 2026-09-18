from dataclasses import dataclass

from src.modules.auth.public.user_id import UserId
from src.modules.journal.public.journal_entry_id import JournalEntryId


@dataclass(frozen=True, slots=True)
class DeleteJournalEntryInputDTO:
    journal_entry_id: JournalEntryId
    user_id: UserId
