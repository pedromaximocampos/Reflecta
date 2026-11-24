from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class JournalDataExport:
    entries: tuple[dict[str, Any], ...]
    context_analyses: tuple[dict[str, Any], ...]


class IJournalDataExportFacade(Protocol):
    async def export_journal(self, user_id: str) -> JournalDataExport: ...
