from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ThemeValidator(BaseModel):
    """Request validator for one canonical theme."""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., description="Theme name", min_length=3, max_length=50)
    description: str = Field(
        ...,
        description="Theme description",
        min_length=3,
        max_length=255,
    )
    is_active: bool = Field(default=True, description="Whether the theme is active")


class CreateThemesValidator(BaseModel):
    """Request validator for a non-empty theme batch."""

    model_config = ConfigDict(extra="forbid")

    themes: list[ThemeValidator] = Field(
        ...,
        description="List of themes to create",
        min_length=1,
    )


class CreatedThemeValidator(ThemeValidator):
    id: str
    slug: str
    created_at: datetime
    updated_at: datetime | None = None


class CreateThemesResponseValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    themes: list[CreatedThemeValidator] = Field(..., min_length=1)


class ThemesResponseValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    themes: list[CreatedThemeValidator]
