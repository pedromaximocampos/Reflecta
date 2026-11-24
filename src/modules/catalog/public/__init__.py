"""Stable catalog contracts available to other modules."""

from .contextual_passage import (
    ContextualPassageCandidate,
    IContextualPassageCatalog,
)
from .passage_candidate import PassageSuggestion, PassageThemeSuggestion
from .passage_id import PassageId
from .recommendation_work import (
    IRecommendationWorkCatalog,
    RecommendationWork,
    RecommendationWorkPage,
)
from .work_ingestion_summary import WorkIngestionSummary

__all__ = [
    "ContextualPassageCandidate",
    "IContextualPassageCatalog",
    "IRecommendationWorkCatalog",
    "PassageId",
    "PassageSuggestion",
    "PassageThemeSuggestion",
    "RecommendationWork",
    "RecommendationWorkPage",
    "WorkIngestionSummary",
]
