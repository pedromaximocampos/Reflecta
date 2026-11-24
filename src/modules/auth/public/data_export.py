from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ExportedAvatar:
    filename: str
    content_type: str
    content: bytes


@dataclass(frozen=True, slots=True)
class AccountDataExport:
    profile: dict[str, Any]
    avatar: ExportedAvatar | None = None
    warnings: tuple[str, ...] = ()


class AccountDataExportUnavailable(Exception):
    """The authenticated account is no longer available for export."""


class IAccountDataExportFacade(Protocol):
    async def export_account(self, user_id: str) -> AccountDataExport: ...
