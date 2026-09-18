from pydantic import BaseModel, ConfigDict, Field, field_validator


class UpdateThemeValidator(BaseModel):
    """Request validator for a partial canonical-theme update."""

    model_config = ConfigDict(extra="forbid")

    label: str | None = Field(default=None, min_length=3, max_length=50)
    description: str | None = Field(default=None, min_length=3, max_length=255)
    is_active: bool | None = None

    @field_validator("label", "description", "is_active", mode="before")
    @classmethod
    def reject_explicit_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("Explicit null is not allowed; omit unchanged fields.")
        return value
