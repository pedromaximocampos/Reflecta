from dataclasses import dataclass

from src.modules.catalog.application.dto.theme import (
    ThemeOutputDTO,
    ThemesOutputDTO,
)


@dataclass(slots=True)
class CreateThemeInputDTO:
    label: str
    description: str
    is_active: bool = True


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


CreateThemeOutputDTO = ThemeOutputDTO
CreateThemesOutputDTO = ThemesOutputDTO
