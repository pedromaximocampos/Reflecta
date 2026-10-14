from dataclasses import dataclass
from datetime import datetime

from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.domain.value_objects.catalog_status import CatalogStatus
from src.modules.catalog.public.author_id import AuthorId
from src.modules.catalog.public.work_id import WorkId


@dataclass(frozen=True, slots=True)
class AuthorOutputDTO:
    id: AuthorId
    name: str
    normalized_name: str
    description: str

    @classmethod
    def from_entity(cls, author: Author) -> "AuthorOutputDTO":
        return cls(author.id, author.name, author.normalized_name, author.description)

    def to_dict(self) -> dict:
        return {
            "id": self.id.value,
            "name": self.name,
            "normalized_name": self.normalized_name,
            "description": self.description,
        }


@dataclass(frozen=True, slots=True)
class WorkOutputDTO:
    id: WorkId
    slug: str
    title: str
    synopsis: str
    work_type: str
    language: str
    status: CatalogStatus
    author: AuthorOutputDTO
    created_at: datetime
    cover_image_url: str | None = None
    source_file_url: str | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_entities(cls, work: Work, author: Author) -> "WorkOutputDTO":
        return cls(
            id=work.id,
            slug=work.slug,
            title=work.title,
            synopsis=work.synopsis,
            work_type=work.work_type,
            language=work.language,
            status=work.status,
            author=AuthorOutputDTO.from_entity(author),
            created_at=work.created_at,
            cover_image_url=work.cover_image_url,
            source_file_url=work.source_file_url,
            updated_at=work.updated_at,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id.value,
            "slug": self.slug,
            "title": self.title,
            "synopsis": self.synopsis,
            "type": self.work_type,
            "language": self.language,
            "status": self.status.value,
            "author": self.author.to_dict(),
            "cover_image_url": self.cover_image_url,
            "source_file_url": self.source_file_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
