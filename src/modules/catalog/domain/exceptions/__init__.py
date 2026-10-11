"""Catalog domain exceptions."""
from src.modules.catalog.domain.exceptions.theme_exceptions import (
    EmptyThemeUpdateError,
    EmptyThemeBatchError,
    InvalidThemeSlugError,
    ThemeAlreadyExistsError,
    ThemeNotFoundError,
)
from src.modules.catalog.domain.exceptions.passage_exceptions import (
    EmptyPassageUpdateError,
    InactivePassageThemeError,
    InvalidPassageThemesError,
    InvalidPassageTransitionError,
    PassageNotFoundError,
)

__all__ = [
    "EmptyThemeBatchError",
    "EmptyThemeUpdateError",
    "InvalidThemeSlugError",
    "ThemeAlreadyExistsError",
    "ThemeNotFoundError",
    "EmptyPassageUpdateError",
    "InactivePassageThemeError",
    "InvalidPassageThemesError",
    "InvalidPassageTransitionError",
    "PassageNotFoundError",
]
