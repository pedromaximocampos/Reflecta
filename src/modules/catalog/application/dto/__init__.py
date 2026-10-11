"""Data transfer objects shared by catalog application use cases."""

from src.modules.catalog.application.dto.theme import (
    ThemeOutputDTO,
    ThemesOutputDTO,
)
from .stored_work_document import StoredWorkDocumentDTO
from .passage import PassageOutputDTO, PassagesOutputDTO, PassageThemeOutputDTO

__all__ = (
    "PassageOutputDTO",
    "PassagesOutputDTO",
    "PassageThemeOutputDTO",
    "StoredWorkDocumentDTO",
    "ThemeOutputDTO",
    "ThemesOutputDTO",
)
