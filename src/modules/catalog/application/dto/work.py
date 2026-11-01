from dataclasses import dataclass, field
from datetime import datetime

from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.domain.ports.repositories.iwork_repository import (
    WorkCatalogRecord,
)
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
class WorkPassageCountsOutputDTO:
    total: int = 0
    active: int = 0
    inactive: int = 0

    def to_dict(self) -> dict:
        return {
            "total": self.total,
            "active": self.active,
            "inactive": self.inactive,
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
    passage_counts: WorkPassageCountsOutputDTO = field(
        default_factory=WorkPassageCountsOutputDTO
    )
    cover_image_url: str | None = None
    source_file_url: str | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_entities(
        cls,
        work: Work,
        author: Author,
        cover_image_url: str | None = None,
    ) -> "WorkOutputDTO":
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
            cover_image_url=cover_image_url or work.cover_image_url,
            source_file_url=work.source_file_url,
            updated_at=work.updated_at,
        )

    @classmethod
    def from_catalog_record(
        cls,
        record: WorkCatalogRecord,
        cover_image_url: str | None = None,
    ) -> "WorkOutputDTO":
        output = cls.from_entities(
            record.work,
            record.author,
            cover_image_url=cover_image_url,
        )
        return cls(
            id=output.id,
            slug=output.slug,
            title=output.title,
            synopsis=output.synopsis,
            work_type=output.work_type,
            language=output.language,
            status=output.status,
            author=output.author,
            created_at=output.created_at,
            passage_counts=WorkPassageCountsOutputDTO(
                total=record.passage_count,
                active=record.active_passage_count,
                inactive=record.inactive_passage_count,
            ),
            cover_image_url=output.cover_image_url,
            source_file_url=output.source_file_url,
            updated_at=output.updated_at,
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
            "passage_counts": self.passage_counts.to_dict(),
            "cover_image_url": self.cover_image_url,
            "source_file_url": self.source_file_url,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass(frozen=True, slots=True)
class WorksOutputDTO:
    works: tuple[WorkOutputDTO, ...]

    @classmethod
    def from_entities(
        cls,
        records: list[WorkCatalogRecord],
    ) -> "WorksOutputDTO":
        return cls(
            tuple(
                WorkOutputDTO.from_catalog_record(record)
                for record in records
            )
        )

    def to_dict(self) -> dict:
        return {"works": [work.to_dict() for work in self.works]}
