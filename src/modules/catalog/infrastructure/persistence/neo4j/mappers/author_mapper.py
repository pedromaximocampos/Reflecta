from collections.abc import Mapping
from datetime import datetime
from typing import Any

from neo4j.time import DateTime as Neo4jDateTime

from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.public.author_id import AuthorId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class AuthorMapper(IMapper[Mapping[str, Any], Author]):
    def to_entity(self, model: Mapping[str, Any]) -> Author:
        return Author(
            id=AuthorId(model["author_id"]),
            name=model["name"],
            normalized_name=model["normalized_name"],
            description=model["description"],
            created_at=self._to_native_datetime(model["created_at"]),
            updated_at=self._to_optional_native_datetime(model.get("updated_at")),
        )

    def to_model(self, entity: Author) -> Mapping[str, Any]:
        return {
            "author_id": entity.id.value,
            "name": entity.name,
            "normalized_name": entity.normalized_name,
            "description": entity.description,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    @staticmethod
    def _to_native_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, Neo4jDateTime):
            return value.to_native()
        raise TypeError("Author datetime property has an unsupported type.")

    @classmethod
    def _to_optional_native_datetime(cls, value: Any) -> datetime | None:
        return None if value is None else cls._to_native_datetime(value)
