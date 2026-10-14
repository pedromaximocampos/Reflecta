from collections.abc import Mapping
from datetime import datetime
from typing import Any

from neo4j.time import DateTime as Neo4jDateTime

from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.domain.value_objects.catalog_status import CatalogStatus
from src.modules.catalog.public.work_id import WorkId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class WorkMapper(IMapper[Mapping[str, Any], Work]):
    def to_entity(self, model: Mapping[str, Any]) -> Work:
        return Work(
            id=WorkId(model["work_id"]),
            slug=model["slug"],
            title=model["title"],
            synopsis=model["synopsis"],
            work_type=model["type"],
            language=model["language"],
            status=CatalogStatus(model["status"]),
            cover_image_url=model.get("cover_image_url"),
            source_file_url=model.get("source_file_url"),
            created_at=self._to_native_datetime(model["created_at"]),
            updated_at=self._to_optional_native_datetime(model.get("updated_at")),
        )

    def to_model(self, entity: Work) -> Mapping[str, Any]:
        return {
            "work_id": entity.id.value,
            "slug": entity.slug,
            "title": entity.title,
            "synopsis": entity.synopsis,
            "type": entity.work_type,
            "language": entity.language,
            "cover_image_url": entity.cover_image_url,
            "source_file_url": entity.source_file_url,
            "status": entity.status.value,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    @staticmethod
    def _to_native_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, Neo4jDateTime):
            return value.to_native()
        raise TypeError("Work datetime property has an unsupported type.")

    @classmethod
    def _to_optional_native_datetime(cls, value: Any) -> datetime | None:
        return None if value is None else cls._to_native_datetime(value)
