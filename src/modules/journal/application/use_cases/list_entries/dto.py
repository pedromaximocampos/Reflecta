from dataclasses import dataclass

from src.modules.auth.public.user_id import UserId


@dataclass(frozen=True, slots=True)
class ListJournalEntriesInputDTO:
    user_id: UserId
    limit: int = 50
    offset: int = 0
