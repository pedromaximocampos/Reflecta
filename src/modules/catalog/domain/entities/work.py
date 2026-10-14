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
    cover_image_url: str | None = None
    source_file_url: str | None = None
    updated_at: datetime | None = None
