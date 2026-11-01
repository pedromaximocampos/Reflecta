from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class CreateAuthorValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., min_length=2, max_length=160)
    description: str = Field(default="", max_length=1000)


class CreateWorkValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str = Field(..., min_length=1, max_length=255)
    synopsis: str = Field(..., min_length=1, max_length=4000)
    type: str = Field(..., min_length=2, max_length=50)
    language: str = Field(..., min_length=2, max_length=35)
    author: CreateAuthorValidator


class CreatedAuthorValidator(CreateAuthorValidator):
    id: str
    normalized_name: str


class WorkPassageCountsValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")
    total: int = Field(default=0, ge=0)
    active: int = Field(default=0, ge=0)
    inactive: int = Field(default=0, ge=0)


class CreatedWorkValidator(CreateWorkValidator):
    id: str
    slug: str
    status: str
    author: CreatedAuthorValidator
    passage_counts: WorkPassageCountsValidator = Field(
        default_factory=WorkPassageCountsValidator
    )
    cover_image_url: str | None = None
    source_file_url: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class WorksResponseValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")
    works: list[CreatedWorkValidator]
