from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.modules.catalog.public.theme_id import ThemeId


@dataclass(slots=True)
class CreateThemesInputDTO:
    themes: list[CreateThemeInputDTO]

    @classmethod
    def to_class(cls, data: dict) -> "CreateThemesInputDTO":
        themes = [
            CreateThemeInputDTO(
                label=theme["label"],
                description=theme["description"],
                is_active=theme.get("is_active", True),
            )
            for theme in data.get("themes", [])
        ]
        return cls(themes=themes)


@dataclass(slots=True)
class CreateThemeInputDTO:
    label: str
    description: str
    is_active: Optional[bool] = True


@dataclass(slots=True)
class CreateThemesOutputDTO:
    themes: list[CreateThemeOutputDTO]


    @classmethod
    def to_dict(cls, output_dto: "CreateThemesOutputDTO") -> dict:
        return {
            "themes": [
                {
                    "id": theme.id.value,
                    "slug": theme.slug,
                    "label": theme.label,
                    "description": theme.description,
                    "is_active": theme.is_active,
                    "created_at": theme.created_at.isoformat(),
                    "updated_at": theme.updated_at.isoformat() if theme.updated_at else None,
                }
                for theme in output_dto.themes
            ]
        }

    @classmethod
    def to_class(cls, themes: list[dict]) -> "CreateThemesOutputDTO":
        themes = [
            CreateThemeOutputDTO(
                id=ThemeId(value=theme["id"]),
                slug=theme["slug"],
                label=theme["label"],
                description=theme["description"],
                is_active=theme["is_active"],
                created_at=datetime.fromisoformat(theme["created_at"]),
                updated_at=datetime.fromisoformat(theme["updated_at"]) if theme.get("updated_at") else None,
            )
            for theme in themes
        ]
        return cls(themes=themes)

@dataclass(slots=True)
class CreateThemeOutputDTO:
    id: ThemeId
    slug: str
    label: str
    description: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

