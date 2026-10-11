from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SuggestedPassageThemeDTO:
    theme_id: str
    confidence: float

    def __post_init__(self) -> None:
        if not self.theme_id.strip():
            raise ValueError("Suggested passage theme ID must not be empty.")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "Suggested passage theme confidence must be between 0 and 1."
            )


@dataclass(frozen=True, slots=True)
class SuggestedPassageDTO:
    exact_text: str
    chunk_start_offset: int
    chunk_end_offset: int
    paraphrase: str
    rationale: str
    themes: tuple[SuggestedPassageThemeDTO, ...]

    def __post_init__(self) -> None:
        if not self.exact_text.strip():
            raise ValueError("Suggested passage text must not be empty.")
        if (
            self.chunk_start_offset < 0
            or self.chunk_end_offset <= self.chunk_start_offset
        ):
            raise ValueError("Suggested passage offsets are invalid.")
        if not self.paraphrase.strip() or not self.rationale.strip():
            raise ValueError("Suggested passage explanation must not be empty.")
        theme_ids = tuple(theme.theme_id for theme in self.themes)
        if not theme_ids or len(theme_ids) != len(set(theme_ids)):
            raise ValueError("Suggested passage themes must be non-empty and unique.")


@dataclass(frozen=True, slots=True)
class WorkChunkAnalysisDTO:
    passages: tuple[SuggestedPassageDTO, ...]
