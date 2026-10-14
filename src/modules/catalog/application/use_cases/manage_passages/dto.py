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
    short_text: str | None = None
    paraphrase: str | None = None
    interpretation_note: str | None = None
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
                self.short_text,
                self.paraphrase,
                self.interpretation_note,
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
