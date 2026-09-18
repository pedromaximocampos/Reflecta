from dataclasses import dataclass

from src.modules.catalog.public.theme_id import ThemeId


@dataclass(frozen=True, slots=True)
class UpdateThemeInputDTO:
    theme_id: ThemeId
    label: str | None = None
    description: str | None = None
    is_active: bool | None = None
