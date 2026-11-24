from dataclasses import dataclass
from datetime import date
from typing import Protocol

from src.modules.auth.public.user_id import UserId
from src.modules.journal.domain.entities.journal_entry import JournalEntry
from src.modules.journal.public.journal_entry_id import JournalEntryId


@dataclass(frozen=True, slots=True)
class JournalEntryWindow:
    entries: tuple[JournalEntry, ...]
    start_date: date | None
    end_date: date | None
    next_end_date: date | None


@dataclass(frozen=True, slots=True)
class JournalEntryCalendarItem:
    id: JournalEntryId
    entry_date: date
    status: str


class IJournalEntryRepository(Protocol):
    async def create(self, journal_entry: JournalEntry) -> JournalEntry: ...

    async def find_by_id_for_user(
        self,
        journal_entry_id: JournalEntryId,
        user_id: UserId,
    ) -> JournalEntry | None: ...

    async def find_by_date_for_user(
        self,
        entry_date: date,
        user_id: UserId,
    ) -> JournalEntry | None: ...

    async def list_by_user(
        self,
        user_id: UserId,
        *,
        limit: int,
        offset: int,
    ) -> list[JournalEntry]: ...

    async def list_window_by_user(
        self,
        user_id: UserId,
        *,
        end_date: date | None,
        days: int,
        center_date: date | None = None,
        before_days: int = 15,
        after_days: int = 15,
    ) -> JournalEntryWindow: ...

    async def list_calendar_by_user(
        self,
        user_id: UserId,
        *,
        start_date: date,
        end_date: date,
    ) -> tuple[JournalEntryCalendarItem, ...]: ...

    async def update(
        self,
        journal_entry: JournalEntry,
        fields_to_update: frozenset[str],
    ) -> JournalEntry: ...

    async def soft_delete(self, journal_entry: JournalEntry) -> None: ...
