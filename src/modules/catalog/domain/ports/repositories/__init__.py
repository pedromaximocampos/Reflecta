"""Abstract repositories owned by the catalog module."""
from .itheme_repository import IThemeRepository
from .ipassage_repository import IPassageRepository
from .iwork_ingestion_repository import IWorkIngestionRepository
from .iwork_repository import IWorkRepository

__all__ = (
    "IPassageRepository",
    "IThemeRepository",
    "IWorkIngestionRepository",
    "IWorkRepository",
)
