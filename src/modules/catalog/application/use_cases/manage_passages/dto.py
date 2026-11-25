from dataclasses import dataclass

from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.theme_id import ThemeId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(frozen=True, slots=True)
class PassageThemeInputDTO:
    theme_id: ThemeId
    confidence: float


@dataclass(frozen=True, slots=True)
class CreatePassageInputDTO:
    work_id: WorkId
    locator: str
    short_text: str
    paraphrase: str
    interpretation_note: str
    priority: int
    themes: tuple[PassageThemeInputDTO, ...]
    start_page: int | None = None
    end_page: int | None = None


@dataclass(frozen=True, slots=True)
class UpdatePassageInputDTO:
    passage_id: PassageId
    locator: str | None = None
    paraphrase: str | None = None
    priority: int | None = None
    themes: tuple[PassageThemeInputDTO, ...] | None = None
    start_page: int | None = None
    end_page: int | None = None
    update_page_range: bool = False

    def is_empty(self) -> bool:
        return all(
            value is None
            for value in (
                self.locator,
                self.paraphrase,
                self.priority,
                self.themes,
                self.start_page,
                self.end_page,
            )
        ) and not self.update_page_range


@dataclass(frozen=True, slots=True)
class ListPassagesInputDTO:
    status: CatalogStatus | None = None
    work_id: WorkId | None = None
    ingestion_id: WorkIngestionId | None = None
    work_title: str | None = None
    author_name: str | None = None
    confidence_min: float | None = None
    confidence_max: float | None = None
    limit: int = 30
    offset: int = 0

    def __post_init__(self) -> None:
        if not 1 <= self.limit <= 100 or self.offset < 0:
            raise ValueError("Invalid passage pagination.")
        for confidence in (self.confidence_min, self.confidence_max):
            if confidence is not None and not 0 <= confidence <= 1:
                raise ValueError("Invalid passage confidence range.")
        if (
            self.confidence_min is not None
            and self.confidence_max is not None
            and self.confidence_min >= self.confidence_max
        ):
            raise ValueError("Invalid passage confidence range.")
