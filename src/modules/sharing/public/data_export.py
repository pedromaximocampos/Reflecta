from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class SharingDataExport:
    shares: tuple[dict[str, Any], ...]
    professional_activities: tuple[dict[str, Any], ...]


class ISharingDataExportFacade(Protocol):
    async def export_sharing(
        self,
        user_id: str,
        *,
        generated_at: datetime,
    ) -> SharingDataExport: ...
