from collections.abc import Mapping
from datetime import datetime
from typing import Any

from neo4j.time import DateTime as Neo4jDateTime

from src.modules.catalog.domain.entities.passage import (
    Passage,
    PassageThemeRelevance,
)
from src.modules.catalog.domain.value_objects import CatalogStatus
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.theme_id import ThemeId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class PassageMapper(IMapper[Mapping[str, Any], Passage]):
    def to_entity(self, model: Mapping[str, Any]) -> Passage:
        ingestion_id = model.get("ingestion_id")
        return Passage(
            id=PassageId(model["passage_id"]),
            work_id=WorkId(model["work_id"]),
            source_key=model["source_key"],
            locator=model["locator"],
            short_text=model["short_text"],
            paraphrase=model["paraphrase"],
            interpretation_note=model["interpretation_note"],
            status=CatalogStatus(model["status"]),
            priority=model["priority"],
            themes=tuple(
                PassageThemeRelevance(
                    theme_id=ThemeId(item["theme_id"]),
                    confidence=item["confidence"],
                )
                for item in model.get("themes", ())
            ),
            created_at=self._to_native_datetime(model["created_at"]),
            ingestion_id=(
                WorkIngestionId(ingestion_id) if ingestion_id is not None else None
            ),
            source_chunk_id=model.get("source_chunk_id"),
            source=model.get("source")
            or ("ai" if ingestion_id is not None else "admin"),
            start_page=model.get("start_page"),
            end_page=model.get("end_page"),
            start_offset=model.get("start_offset"),
            end_offset=model.get("end_offset"),
            updated_at=self._to_optional_native_datetime(model.get("updated_at")),
        )

    def to_model(self, entity: Passage) -> Mapping[str, Any]:
        return {
            "passage_id": entity.id.value,
            "work_id": entity.work_id.value,
            "ingestion_id": (
                entity.ingestion_id.value if entity.ingestion_id is not None else None
            ),
            "source_chunk_id": entity.source_chunk_id,
            "source_key": entity.source_key,
            "source": entity.source,
            "locator": entity.locator,
            "short_text": entity.short_text,
            "paraphrase": entity.paraphrase,
            "interpretation_note": entity.interpretation_note,
            "status": entity.status.value,
            "priority": entity.priority,
            "start_page": entity.start_page,
            "end_page": entity.end_page,
            "start_offset": entity.start_offset,
            "end_offset": entity.end_offset,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    @staticmethod
    def _to_native_datetime(value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, Neo4jDateTime):
            return value.to_native()
        raise TypeError("Passage datetime property has an unsupported type.")

    @classmethod
    def _to_optional_native_datetime(cls, value: Any) -> datetime | None:
        return None if value is None else cls._to_native_datetime(value)
