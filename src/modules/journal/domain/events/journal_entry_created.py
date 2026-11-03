from dataclasses import dataclass
from datetime import datetime

from src.modules.auth.public.user_id import UserId
from src.modules.journal.public.journal_entry_id import JournalEntryId


@dataclass(frozen=True, slots=True)
class JournalEntryCreated:
    """Internal event; carries identifiers only, never the journal text."""

    entry_id: JournalEntryId
    user_id: UserId
    occurred_at: datetime
