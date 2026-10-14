from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PassageThemeSuggestion:
    theme_id: str
    confidence: float


@dataclass(frozen=True, slots=True)
class PassageSuggestion:
    exact_text: str
    paraphrase: str
    interpretation_note: str
    start_page: int
    end_page: int
    start_offset: int
    end_offset: int
    themes: tuple[PassageThemeSuggestion, ...]
