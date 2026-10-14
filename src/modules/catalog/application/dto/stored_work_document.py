from dataclasses import dataclass

from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)


@dataclass(frozen=True, slots=True)
class StoredWorkDocumentDTO:
    location: WorkDocumentLocation
    content_type: str
    size_bytes: int
    etag: str | None = None
    version_id: str | None = None
