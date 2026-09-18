from collections.abc import Mapping
from datetime import datetime
from typing import Any

from neo4j.time import DateTime as Neo4jDateTime

from src.modules.catalog.domain.entities.theme import Theme
from src.modules.catalog.public.theme_id import ThemeId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class ThemeMapper(IMapper[Mapping[str, Any], Theme]):
    def to_entity(self, model: Mapping[str, Any]) -> Theme:
        return Theme(
            id=ThemeId(model["theme_id"]),
            slug=model["slug"],
            label=model["label"],
            description=model["description"],
            is_active=model["is_active"],
            created_at=self._to_native_datetime(model["created_at"]),
            updated_at=self._to_optional_native_datetime(model.get("updated_at")),
        )

    def to_model(self, entity: Theme) -> Mapping[str, Any]:
        return {
            "theme_id": entity.id.value,
            "slug": entity.slug,
            "label": entity.label,
            "description": entity.description,
            "is_active": entity.is_active,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    @staticmethod
    def _to_native_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, Neo4jDateTime):
            return value.to_native()
        raise TypeError("Theme datetime property has an unsupported type.")

    @classmethod
    def _to_optional_native_datetime(cls, value: Any) -> datetime | None:
        if value is None:
            return None
        return cls._to_native_datetime(value)
