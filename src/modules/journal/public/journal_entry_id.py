from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class JournalEntryId:
    value: str
