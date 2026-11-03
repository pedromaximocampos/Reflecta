from .failure_reasons import FailureReason
from pathlib import Path
from typing import Annotated, Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from src.modules.catalog.public.analysis_theme import ThemeOption

Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10000)]
MAX_SELECTED_THEMES = 5
MIN_THEME_CONFIDENCE = 0.80


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class ThemeMatch(StrictModel):
    theme_id: Text
    confidence: float = Field(
        ge=MIN_THEME_CONFIDENCE,
        le=1,
        allow_inf_nan=False,
    )


class SentenceInterpretation(StrictModel):
    sentence_text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20000)]
    themes: list[ThemeMatch] = Field(max_length=MAX_SELECTED_THEMES)


class Interpretation(StrictModel):
    summary: Text
    main_message: Text
    themes: list[ThemeMatch] = Field(max_length=MAX_SELECTED_THEMES)
    sentiments: list[Text] = Field(max_length=20)
    tone: Text
    sentences: list[SentenceInterpretation] = Field(min_length=1, max_length=500)


class InterpretationRequest(StrictModel):
    content_text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20000)]
    context_tags: dict[str, Any] | None
    themes: tuple[ThemeOption, ...]
    instructions: str = Path(__file__).with_name("reflecta_analysis_prompt.md").read_text(encoding="utf-8")


class ITextInterpreter(Protocol):
    def ensure_available(self) -> None: ...

    async def interpret(self, request: InterpretationRequest) -> dict[str, Any]: ...


class IThemeCatalog(Protocol):
    async def active_themes(self) -> tuple[ThemeOption, ...]: ...


class ProviderNotConfiguredError(Exception):
    """Provider/account/model/credentials have not been defined."""


class InterpretationFailedError(Exception):
    """Safe error; diagnosis is an allowlisted code, never provider text."""

    default_reason = FailureReason.INTERPRETATION

    def __init__(self, message="Text interpretation failed.", *, reason=None):
        super().__init__(message)
        self.reason = FailureReason(reason) if reason is not None else self.default_reason


class InvalidInterpretationError(InterpretationFailedError):
    default_reason = FailureReason.INVALID_RESULT


class InvalidJournalInputError(Exception):
    """Input rejected without including journal text in the error."""
