from dataclasses import dataclass
from datetime import date

from src.modules.auth.public.user_id import UserId


@dataclass(frozen=True, slots=True)
class ListJournalEntryCalendarInputDTO:
    user_id: UserId
    start_date: date
    end_date: date


@dataclass(frozen=True, slots=True)
class JournalEntryCalendarItemOutputDTO:
    id: str
    entry_date: date
    status: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "entry_date": self.entry_date.isoformat(),
            "status": self.status,
        }


@dataclass(frozen=True, slots=True)
class JournalEntryCalendarOutputDTO:
    entries: tuple[JournalEntryCalendarItemOutputDTO, ...]
    start_date: date
    end_date: date

    def to_dict(self) -> dict:
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }
