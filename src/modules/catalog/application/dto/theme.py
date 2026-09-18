from dataclasses import dataclass
from datetime import datetime

from src.modules.catalog.domain.entities.theme import Theme
from src.modules.catalog.public.theme_id import ThemeId


@dataclass(frozen=True, slots=True)
class ThemeOutputDTO:
    id: ThemeId
    slug: str
    label: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None

    @classmethod
    def from_entity(cls, theme: Theme) -> "ThemeOutputDTO":
        return cls(
            id=theme.id,
            slug=theme.slug,
            label=theme.label,
            description=theme.description,
            is_active=theme.is_active,
            created_at=theme.created_at,
            updated_at=theme.updated_at,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id.value,
            "slug": self.slug,
            "label": self.label,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass(frozen=True, slots=True)
class ThemesOutputDTO:
    themes: list[ThemeOutputDTO]

    @classmethod
    def from_entities(cls, themes: list[Theme]) -> "ThemesOutputDTO":
        return cls(themes=[ThemeOutputDTO.from_entity(theme) for theme in themes])

    def to_dict(self) -> dict:
        return {"themes": [theme.to_dict() for theme in self.themes]}
