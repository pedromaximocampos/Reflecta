from dataclasses import dataclass
from datetime import datetime

from src.modules.catalog.domain.value_objects.catalog_status import CatalogStatus
from src.modules.catalog.public.work_id import WorkId


@dataclass(eq=False, slots=True)
class Work:
    id: WorkId
    slug: str
    title: str
    synopsis: str
    work_type: str
    language: str
    status: CatalogStatus
    created_at: datetime
    cover_object_key: str | None = None
    # Compatibility with works created before managed S3 cover uploads.
    cover_image_url: str | None = None
    source_file_url: str | None = None
    updated_at: datetime | None = None

    def replace_cover(
        self,
        cover_object_key: str,
        updated_at: datetime,
    ) -> None:
        self.cover_object_key = cover_object_key
        self.cover_image_url = None
        self.updated_at = updated_at

    def remove_cover(self, updated_at: datetime) -> None:
        self.cover_object_key = None
        self.cover_image_url = None
        self.updated_at = updated_at
