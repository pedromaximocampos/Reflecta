from collections.abc import Mapping
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator
from src.modules.catalog.public.theme_color import ThemeColor


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

    @model_validator(mode="before")
    @classmethod
    def discard_legacy_color(cls, value: Any) -> Any:
        """Accept old clients without allowing them to choose the theme color."""
        if not isinstance(value, Mapping):
            return value

        payload = dict(value)
        payload.pop("color", None)
        return payload


class CreateThemesValidator(BaseModel):
    """Request validator for a non-empty theme batch."""

    model_config = ConfigDict(extra="forbid")

    themes: list[ThemeValidator] = Field(
        ...,
        description="List of themes to create",
        min_length=1,
    )


class CreatedThemeValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    slug: str
    label: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., min_length=3, max_length=255)
    is_active: bool
    color: ThemeColor
    created_at: datetime
    updated_at: datetime | None = None


class CreateThemesResponseValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    themes: list[CreatedThemeValidator] = Field(..., min_length=1)


class ThemesResponseValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    themes: list[CreatedThemeValidator]
