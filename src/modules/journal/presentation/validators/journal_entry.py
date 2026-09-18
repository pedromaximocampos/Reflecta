from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from src.modules.journal.domain.value_objects.content_tags import TagSource
from src.modules.journal.domain.value_objects.journal_entry_status import (
    JournalEntryStatus,
)


class ContextTagItemValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., min_length=1, max_length=100)
    source: TagSource = TagSource.USER
    confidence: float | None = Field(default=None, ge=0, le=1)
    approved: bool | None = None

    @field_validator("label")
    @classmethod
    def normalize_label(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Tag label cannot be empty.")
        return normalized


class ContextTagsValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    people: list[ContextTagItemValidator] = Field(default_factory=list)
    places: list[ContextTagItemValidator] = Field(default_factory=list)
    domains: list[ContextTagItemValidator] = Field(default_factory=list)


class CreateJournalEntryValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=200)
    content_text: str = Field(..., min_length=1, max_length=20_000)
    context_tags: ContextTagsValidator | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("content_text")
    @classmethod
    def normalize_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Journal content cannot be empty.")
        return normalized


class UpdateJournalEntryValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=200)
    content_text: str | None = Field(default=None, min_length=1, max_length=20_000)
    context_tags: ContextTagsValidator | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("content_text")
    @classmethod
    def normalize_content(cls, value: str | None) -> str | None:
        if value is None:
            raise ValueError("content_text cannot be null.")
        normalized = value.strip()
        if not normalized:
            raise ValueError("Journal content cannot be empty.")
        return normalized

    @model_validator(mode="after")
    def validate_partial_update(self):
        if not self.model_fields_set:
            raise ValueError("Provide at least one field for update.")
        return self


class JournalEntryResponseValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    user_id: str
    title: str | None
    content_text: str
    context_tags: dict | None
    status: JournalEntryStatus
    created_at: datetime
    updated_at: datetime | None


class JournalEntriesResponseValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entries: list[JournalEntryResponseValidator]
