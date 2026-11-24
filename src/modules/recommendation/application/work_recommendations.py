from typing import Any

from src.modules.catalog.public import (
    IContextualPassageCatalog,
    IRecommendationWorkCatalog,
    RecommendationWork,
)
from src.modules.journal.public.dashboard import IJournalInsightsReader


class RecommendWorks:
    """Ranks catalog works from the user's recurring journal themes.

    The score is deterministic and explainable. For each work and theme, only
    the strongest active passage match contributes, so works with many passages
    do not win merely because of volume.
    """

    def __init__(
        self,
        journal: IJournalInsightsReader,
        catalog: IContextualPassageCatalog,
        works: IRecommendationWorkCatalog,
    ) -> None:
        self.journal = journal
        self.catalog = catalog
        self.works = works

    async def execute(
        self,
        user_id: str,
        *,
        limit: int = 4,
        offset: int = 0,
    ) -> dict[str, Any]:
        if not 1 <= limit <= 12 or offset < 0:
            raise ValueError("Invalid recommendation pagination.")

        affinities = await self.journal.theme_affinities(user_id, limit=5)
        if not affinities:
            return {
                "recommendations": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
            }

        candidates = await self.catalog.find_active_by_themes(
            tuple(item["theme_id"] for item in affinities),
            limit_per_theme=10,
        )
        affinity_by_id = {item["theme_id"]: item for item in affinities}
        works: dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            work = works.setdefault(
                candidate.work_id,
                {
                    "work_id": candidate.work_id,
                    "title": candidate.work_title,
                    "author_name": candidate.author_name,
                    "passage_ids": set(),
                    "theme_confidences": {},
                    "sample_passage": None,
                    "sample_confidence": -1.0,
                },
            )
            work["passage_ids"].add(candidate.passage_id)
            current = work["theme_confidences"].get(
                candidate.matched_theme_id,
                0.0,
            )
            work["theme_confidences"][candidate.matched_theme_id] = max(
                current,
                candidate.matched_theme_confidence,
            )
            if candidate.matched_theme_confidence > work["sample_confidence"]:
                work["sample_confidence"] = candidate.matched_theme_confidence
                work["sample_passage"] = candidate.short_text

        recommendations = []
        for work in works.values():
            score = sum(
                affinity_by_id[theme_id]["reflection_count"] * confidence
                for theme_id, confidence in work["theme_confidences"].items()
            )
            matched_themes = sorted(
                (
                    {
                        **affinity_by_id[theme_id],
                        "catalog_confidence": confidence,
                    }
                    for theme_id, confidence in work["theme_confidences"].items()
                ),
                key=lambda item: (
                    -item["reflection_count"],
                    -item["catalog_confidence"],
                    item["label"].casefold(),
                ),
            )
            recommendations.append({
                "work_id": work["work_id"],
                "title": work["title"],
                "author_name": work["author_name"],
                "score": round(score, 4),
                "matched_themes": matched_themes,
                "active_passage_count": len(work["passage_ids"]),
                "sample_passage": work["sample_passage"],
            })

        recommendations.sort(
            key=lambda item: (-item["score"], item["title"].casefold(), item["work_id"])
        )
        recommendations = recommendations[offset : offset + limit]
        work_details = await self.works.find_by_ids(
            tuple(item["work_id"] for item in recommendations)
        )
        details_by_id = {work.work_id: work for work in work_details}
        for recommendation in recommendations:
            details = details_by_id.get(recommendation["work_id"])
            recommendation["cover_image_url"] = (
                details.cover_image_url if details else None
            )
            recommendation["synopsis"] = details.synopsis if details else ""
            if details:
                recommendation["title"] = details.title
                recommendation["author_name"] = details.author_name
                recommendation["active_passage_count"] = (
                    details.active_passage_count
                )
        return {
            "recommendations": recommendations,
            "total": len(works),
            "limit": limit,
            "offset": offset,
        }


class ExploreWorks:
    """Lists active catalog works independently from journal affinity."""

    def __init__(self, works: IRecommendationWorkCatalog) -> None:
        self.works = works

    async def execute(
        self,
        *,
        limit: int = 6,
        offset: int = 0,
    ) -> dict[str, Any]:
        page = await self.works.list_active(limit=limit, offset=offset)
        return {
            "works": [self._serialize(work) for work in page.works],
            "total": page.total,
            "limit": page.limit,
            "offset": page.offset,
        }

    @staticmethod
    def _serialize(work: RecommendationWork) -> dict[str, Any]:
        return _serialize_work(work)


class GetRecommendationWork:
    """Returns the safe, read-only details of an active catalog work."""

    def __init__(self, works: IRecommendationWorkCatalog) -> None:
        self.works = works

    async def execute(self, work_id: str) -> dict[str, Any] | None:
        if not work_id.strip():
            raise ValueError("Work ID must not be empty.")
        works = await self.works.find_by_ids((work_id,))
        if not works or works[0].active_passage_count <= 0:
            return None
        return _serialize_work(works[0])


def _serialize_work(work: RecommendationWork) -> dict[str, Any]:
    return {
        "work_id": work.work_id,
        "title": work.title,
        "author_name": work.author_name,
        "author_description": work.author_description,
        "work_type": work.work_type,
        "language": work.language,
        "synopsis": work.synopsis,
        "cover_image_url": work.cover_image_url,
        "active_passage_count": work.active_passage_count,
    }

