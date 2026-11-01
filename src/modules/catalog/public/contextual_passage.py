from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class ContextualPassageCandidate(BaseModel):
    """Catalog projection exposed to modules that contextualize journal entries."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    passage_id: str = Field(min_length=1)
    matched_theme_id: str = Field(min_length=1)
    matched_theme_confidence: float = Field(
        ge=0,
        le=1,
        allow_inf_nan=False,
    )
    short_text: str = Field(min_length=1)
    paraphrase: str = Field(min_length=1)
    interpretation_note: str = Field(min_length=1)
    locator: str = Field(min_length=1)
    priority: int = Field(ge=0)
    work_id: str = Field(min_length=1)
    work_title: str = Field(min_length=1)
    author_name: str = Field(min_length=1)
    start_page: int | None = Field(default=None, ge=1)
    end_page: int | None = Field(default=None, ge=1)


class IContextualPassageCatalog(Protocol):
    async def find_active_by_themes(
        self,
        theme_ids: tuple[str, ...],
        *,
        limit_per_theme: int = 5,
    ) -> tuple[ContextualPassageCandidate, ...]: ...

