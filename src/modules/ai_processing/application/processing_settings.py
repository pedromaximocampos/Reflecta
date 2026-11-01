"""Non-secret, validated settings for an administrator's single analysis attempt."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class AnalysisProcessingSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    model: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")
    timeout_seconds: float = Field(ge=1, le=600, allow_inf_nan=False)
    max_output_tokens: int = Field(ge=1, le=128000)
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high", "xhigh", "max"] | None
