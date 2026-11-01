"""Stable catalog contracts available to other modules."""

from .contextual_passage import (
    ContextualPassageCandidate,
    IContextualPassageCatalog,
)
from .passage_candidate import PassageSuggestion, PassageThemeSuggestion
from .passage_id import PassageId
from .work_ingestion_summary import WorkIngestionSummary

__all__ = [
    "ContextualPassageCandidate",
    "IContextualPassageCatalog",
    "PassageId",
    "PassageSuggestion",
    "PassageThemeSuggestion",
    "WorkIngestionSummary",
]
