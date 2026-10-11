"""Application contract for requesting a catalog work ingestion."""

from .dto import (
    RequestWorkIngestionInputDTO,
    RequestWorkIngestionOutputDTO,
)
from .irequest_work_ingestion_use_case import IRequestWorkIngestionUseCase
from .request_work_ingestion_use_case import RequestWorkIngestionUseCase

__all__ = [
    "IRequestWorkIngestionUseCase",
    "RequestWorkIngestionInputDTO",
    "RequestWorkIngestionOutputDTO",
    "RequestWorkIngestionUseCase",
]
