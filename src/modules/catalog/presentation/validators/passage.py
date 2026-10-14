from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PassageThemeInputValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    theme_id: str = Field(..., min_length=26, max_length=26)
    confidence: float = Field(..., ge=0, le=1, allow_inf_nan=False)


class CreatePassageValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    work_id: str = Field(..., min_length=26, max_length=26)
    locator: str = Field(..., min_length=1, max_length=255)
    short_text: str = Field(..., min_length=20, max_length=8000)
    paraphrase: str = Field(..., min_length=1, max_length=4000)
    interpretation_note: str = Field(..., min_length=1, max_length=4000)
    priority: int = Field(default=0, ge=0)
    themes: list[PassageThemeInputValidator] = Field(..., min_length=1)
    start_page: int | None = Field(default=None, ge=1)
    end_page: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_fields(self) -> "CreatePassageValidator":
        if (self.start_page is None) != (self.end_page is None):
            raise ValueError("start_page and end_page must be provided together")
        if (
            self.start_page is not None
            and self.end_page is not None
            and self.end_page < self.start_page
        ):
            raise ValueError("end_page must be greater than or equal to start_page")
        self._validate_unique_themes()
        return self

    def _validate_unique_themes(self) -> None:
        theme_ids = [theme.theme_id for theme in self.themes]
        if len(theme_ids) != len(set(theme_ids)):
            raise ValueError("theme_id values must be unique")


class UpdatePassageValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    locator: str | None = Field(default=None, min_length=1, max_length=255)
    short_text: str | None = Field(default=None, min_length=20, max_length=8000)
    paraphrase: str | None = Field(default=None, min_length=1, max_length=4000)
    interpretation_note: str | None = Field(
        default=None,
        min_length=1,
        max_length=4000,
    )
    priority: int | None = Field(default=None, ge=0)
    themes: list[PassageThemeInputValidator] | None = Field(
        default=None,
        min_length=1,
    )
    start_page: int | None = Field(default=None, ge=1)
    end_page: int | None = Field(default=None, ge=1)

    @model_validator(mode="after")
    def validate_fields(self) -> "UpdatePassageValidator":
        start_page_provided = "start_page" in self.model_fields_set
        end_page_provided = "end_page" in self.model_fields_set
        if start_page_provided != end_page_provided:
            raise ValueError("start_page and end_page must be provided together")
        if (
            self.start_page is not None
            and self.end_page is not None
            and self.end_page < self.start_page
        ):
            raise ValueError("end_page must be greater than or equal to start_page")
        if self.themes is not None:
            theme_ids = [theme.theme_id for theme in self.themes]
            if len(theme_ids) != len(set(theme_ids)):
                raise ValueError("theme_id values must be unique")
        return self


class PassageThemeResponseValidator(PassageThemeInputValidator):
    label: str = Field(..., min_length=1, max_length=120)


class PassageResponseValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    work_id: str
    ingestion_id: str | None = None
    source_chunk_id: str | None = None
    source_key: str
    source: str
    locator: str
    short_text: str
    paraphrase: str
    interpretation_note: str
    status: str
    priority: int
    start_page: int | None = None
    end_page: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    themes: list[PassageThemeResponseValidator]
    created_at: datetime
    updated_at: datetime | None = None


class PassagesResponseValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    passages: list[PassageResponseValidator]
    total: int = Field(..., ge=0)
