from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class SharedTheme(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=120)
    color: str | None = Field(default=None, max_length=32)


class SharedPassage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    short_text: str = Field(min_length=1, max_length=5000)
    work_title: str | None = Field(default=None, max_length=300)
    author_name: str | None = Field(default=None, max_length=300)
    locator: str | None = Field(default=None, max_length=300)
    themes: list[SharedTheme] = Field(default_factory=list, max_length=10)
    reason: str | None = Field(default=None, max_length=5000)
    paraphrase: str | None = Field(default=None, max_length=5000)


class SharedEntryAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conclusion: str | None = Field(default=None, max_length=10000)
    themes: list[SharedTheme] = Field(default_factory=list, max_length=20)
    passages: list[SharedPassage] = Field(default_factory=list, max_length=50)


class SharedJournalEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entry_date: date
    title: str | None = Field(default=None, max_length=200)
    content_text: str = Field(min_length=1, max_length=20000)
    analysis: SharedEntryAnalysis | None = None


def validate_shared_entries(raw_entries) -> list[dict]:
    if not isinstance(raw_entries, list):
        return []
    return [
        SharedJournalEntry.model_validate(entry).model_dump(mode="json")
        for entry in raw_entries
    ]


class JournalShareSourceUnavailable(Exception):
    """The requested analysis does not belong to an available account."""


class JournalShareSourceIneligible(Exception):
    """The analysis exists but cannot produce a valid public snapshot."""


@dataclass(frozen=True, slots=True)
class ShareableContextAnalysis:
    period: dict[str, str]
    created_at: datetime
    entry_count: int
    result: dict
    entries: list[dict]


@dataclass(frozen=True, slots=True)
class ContextAnalysisDescriptor:
    analysis_id: str
    created_at: datetime
    period: dict[str, str] | None
    entry_count: int
    summary: str | None


class IJournalSharingFacade(Protocol):
    async def prepare_share(
        self,
        analysis_id: str,
        user_id: str,
        *,
        include_journals: bool,
    ) -> ShareableContextAnalysis: ...

    async def ensure_available(self, analysis_id: str, user_id: str) -> None: ...

    async def describe_owned(
        self,
        analysis_id: str,
        user_id: str,
    ) -> ContextAnalysisDescriptor: ...

    async def describe_owned_many(
        self,
        analysis_ids: tuple[str, ...],
        user_id: str,
    ) -> dict[str, ContextAnalysisDescriptor]: ...
