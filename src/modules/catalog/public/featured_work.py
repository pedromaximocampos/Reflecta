from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class FeaturedTheme:
    theme_id: str
    label: str
    color: str


@dataclass(frozen=True, slots=True)
class FeaturedPassage:
    short_text: str
    paraphrase: str
    locator: str


@dataclass(frozen=True, slots=True)
class FeaturedWork:
    work_id: str
    title: str
    author_name: str
    synopsis: str
    cover_image_url: str | None
    themes: tuple[FeaturedTheme, ...]
    passage: FeaturedPassage


class IFeaturedWorkCatalog(Protocol):
    async def get_for_day(self, day_ordinal: int) -> FeaturedWork | None: ...
