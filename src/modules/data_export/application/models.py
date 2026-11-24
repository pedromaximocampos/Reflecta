import base64
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.modules.auth.public.data_export import AccountDataExport, ExportedAvatar
from src.modules.journal.public.data_export import JournalDataExport
from src.modules.sharing.public.data_export import SharingDataExport


SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class UserDataExportPackage:
    generated_at: datetime
    account: AccountDataExport
    journal: JournalDataExport
    sharing: SharingDataExport

    @property
    def avatar(self) -> ExportedAvatar | None:
        return self.account.avatar

    @property
    def warnings(self) -> tuple[str, ...]:
        return self.account.warnings

    def manifest(self, *, files: list[str] | None = None) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "generated_at": self.generated_at.isoformat(),
            "counts": {
                "journal_entries": len(self.journal.entries),
                "context_analyses": len(self.journal.context_analyses),
                "shares": len(self.sharing.shares),
                "professional_activities": len(
                    self.sharing.professional_activities
                ),
            },
            "files": files or [],
            "warnings": list(self.warnings),
        }

    def json_document(self) -> dict[str, Any]:
        avatar = None
        if self.avatar is not None:
            avatar = {
                "filename": self.avatar.filename,
                "content_type": self.avatar.content_type,
                "encoding": "base64",
                "content": base64.b64encode(self.avatar.content).decode("ascii"),
            }
        return {
            "manifest": self.manifest(),
            "account": {**self.account.profile, "avatar": avatar},
            "journal": {
                "entries": list(self.journal.entries),
                "context_analyses": list(self.journal.context_analyses),
            },
            "sharing": {
                "shares": list(self.sharing.shares),
                "professional_activities": list(
                    self.sharing.professional_activities
                ),
            },
        }
