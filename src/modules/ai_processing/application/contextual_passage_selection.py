from pathlib import Path
from typing import Annotated, Protocol

from pydantic import Field, StringConstraints

from src.modules.ai_processing.application.contracts import StrictModel, Text
from src.modules.catalog.public.contextual_passage import (
    ContextualPassageCandidate,
)


MIN_PASSAGE_CONFIDENCE = 0.80
MAX_CONTEXTUAL_PASSAGES = 5
ReasonText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=1000),
]


class PassageSelectionTheme(StrictModel):
    theme_id: Text
    label: Text
    description: Text
    confidence: float = Field(ge=0.80, le=1, allow_inf_nan=False)


class PassageSelectionSentence(StrictModel):
    sentence_id: Text
    sentence_text: Text
    themes: tuple[PassageSelectionTheme, ...] = Field(min_length=1, max_length=5)


class ContextualPassageSelectionRequest(StrictModel):
    sentences: tuple[PassageSelectionSentence, ...] = Field(min_length=1)
    candidates: tuple[ContextualPassageCandidate, ...] = Field(min_length=1)
    instructions: str = Path(__file__).with_name(
        "reflecta_passage_selection_prompt.md"
    ).read_text(encoding="utf-8")


class ContextualPassageAssociation(StrictModel):
    sentence_id: Text
    passage_id: Text
    confidence: float = Field(
        ge=MIN_PASSAGE_CONFIDENCE,
        le=1,
        allow_inf_nan=False,
    )
    reason: ReasonText


class ContextualPassageSelection(StrictModel):
    associations: list[ContextualPassageAssociation] = Field(
        max_length=MAX_CONTEXTUAL_PASSAGES,
    )


class IContextualPassageSelector(Protocol):
    def ensure_available(self) -> None: ...

    async def select_contextual_passages(
        self,
        request: ContextualPassageSelectionRequest,
    ) -> dict: ...

