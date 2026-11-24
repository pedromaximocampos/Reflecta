from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RecommendationWork:
    """Public catalog projection safe for recommendation consumers."""

    work_id: str
    title: str
    author_name: str
    synopsis: str
    cover_image_url: str | None
    active_passage_count: int
    work_type: str = ""
    language: str = ""
    author_description: str = ""


@dataclass(frozen=True, slots=True)
class RecommendationWorkPage:
    works: tuple[RecommendationWork, ...]
    total: int
    limit: int
    offset: int


class IRecommendationWorkCatalog(Protocol):
    async def find_by_ids(
        self,
        work_ids: tuple[str, ...],
    ) -> tuple[RecommendationWork, ...]: ...

    async def list_active(
        self,
        *,
        limit: int,
        offset: int,
    ) -> RecommendationWorkPage: ...
