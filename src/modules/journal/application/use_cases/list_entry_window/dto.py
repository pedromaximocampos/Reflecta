from dataclasses import dataclass
from datetime import date

from src.modules.auth.public.user_id import UserId


@dataclass(frozen=True, slots=True)
class ListJournalEntryWindowInputDTO:
    user_id: UserId
    end_date: date | None = None
    days: int = 15
    center_date: date | None = None
    before_days: int = 15
    after_days: int = 15
