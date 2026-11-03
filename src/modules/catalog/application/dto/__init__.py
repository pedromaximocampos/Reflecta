"""Data transfer objects shared by catalog application use cases."""

from src.modules.catalog.application.dto.theme import (
    ThemeOutputDTO,
    ThemesOutputDTO,
)
from .stored_work_document import StoredWorkDocumentDTO
from .processed_work_cover import ProcessedWorkCoverDTO
from .stored_work_cover import StoredWorkCoverDTO
from .passage import PassageOutputDTO, PassagesOutputDTO, PassageThemeOutputDTO
from .work import (
    AuthorOutputDTO,
    WorkOutputDTO,
    WorkPassageCountsOutputDTO,
    WorksOutputDTO,
)

__all__ = (
    "PassageOutputDTO",
    "PassagesOutputDTO",
    "PassageThemeOutputDTO",
    "StoredWorkDocumentDTO",
    "ProcessedWorkCoverDTO",
    "StoredWorkCoverDTO",
    "ThemeOutputDTO",
    "ThemesOutputDTO",
    "AuthorOutputDTO",
    "WorkOutputDTO",
    "WorkPassageCountsOutputDTO",
    "WorksOutputDTO",
)
