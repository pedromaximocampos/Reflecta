from dataclasses import dataclass
from datetime import datetime
from typing import Mapping

from src.modules.catalog.domain.entities.passage import Passage
from src.modules.catalog.public.passage_id import PassageId
from src.modules.catalog.public.theme_id import ThemeId
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(frozen=True, slots=True)
class PassageThemeOutputDTO:
    theme_id: ThemeId
    label: str
    confidence: float

    def to_dict(self) -> dict:
        return {
            "theme_id": self.theme_id.value,
            "label": self.label,
            "confidence": self.confidence,
        }


@dataclass(frozen=True, slots=True)
class PassageOutputDTO:
    id: PassageId
    work_id: WorkId
    source_key: str
    source: str
    locator: str
    short_text: str
    paraphrase: str
    interpretation_note: str
    reflective_value: float | None
    reflective_note: str | None
    status: str
    priority: int
    themes: tuple[PassageThemeOutputDTO, ...]
    created_at: datetime
    ingestion_id: WorkIngestionId | None = None
    source_chunk_id: str | None = None
    start_page: int | None = None
    end_page: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_entity(
        cls,
        passage: Passage,
        theme_labels: Mapping[str, str],
    ) -> "PassageOutputDTO":
        return cls(
            id=passage.id,
            work_id=passage.work_id,
            source_key=passage.source_key,
            source=passage.source,
            locator=passage.locator,
            short_text=passage.short_text,
            paraphrase=passage.paraphrase,
            interpretation_note=passage.interpretation_note,
            reflective_value=passage.reflective_value,
            reflective_note=passage.reflective_note,
            status=passage.status.value,
            priority=passage.priority,
            themes=tuple(
                PassageThemeOutputDTO(
                    theme_id=theme.theme_id,
                    label=theme_labels[theme.theme_id.value],
                    confidence=theme.confidence,
                )
                for theme in passage.themes
            ),
            created_at=passage.created_at,
            ingestion_id=passage.ingestion_id,
            source_chunk_id=passage.source_chunk_id,
            start_page=passage.start_page,
            end_page=passage.end_page,
            start_offset=passage.start_offset,
            end_offset=passage.end_offset,
            updated_at=passage.updated_at,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id.value,
            "work_id": self.work_id.value,
            "ingestion_id": (
                self.ingestion_id.value if self.ingestion_id is not None else None
            ),
            "source_chunk_id": self.source_chunk_id,
            "source_key": self.source_key,
            "source": self.source,
            "locator": self.locator,
            "short_text": self.short_text,
            "paraphrase": self.paraphrase,
            "interpretation_note": self.interpretation_note,
            "reflective_value": self.reflective_value,
            "reflective_note": self.reflective_note,
            "status": self.status,
            "priority": self.priority,
            "start_page": self.start_page,
            "end_page": self.end_page,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "themes": [theme.to_dict() for theme in self.themes],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass(frozen=True, slots=True)
class PassagesOutputDTO:
    passages: tuple[PassageOutputDTO, ...]
    total: int
    limit: int
    offset: int

    @classmethod
    def from_entities(
        cls,
        passages: list[Passage] | tuple[Passage, ...],
        theme_labels: Mapping[str, str],
        *,
        total: int | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> "PassagesOutputDTO":
        effective_total = len(passages) if total is None else total
        effective_limit = len(passages) if limit is None else limit
        return cls(
            passages=tuple(
                PassageOutputDTO.from_entity(item, theme_labels)
                for item in passages
            ),
            total=effective_total,
            limit=effective_limit,
            offset=offset,
        )

    def to_dict(self) -> dict:
        return {
            "passages": [passage.to_dict() for passage in self.passages],
            "total": self.total,
            "limit": self.limit,
            "offset": self.offset,
            "has_more": self.offset + len(self.passages) < self.total,
        }


@dataclass(frozen=True, slots=True)
class PassageStatusCountsOutputDTO:
    total: int
    by_status: Mapping[str, int]

    @classmethod
    def from_counts(
        cls,
        counts: Mapping[str, int],
    ) -> "PassageStatusCountsOutputDTO":
        normalized = {str(status): int(total) for status, total in counts.items()}
        return cls(total=sum(normalized.values()), by_status=normalized)

    def to_dict(self) -> dict:
        return {"total": self.total, "by_status": dict(self.by_status)}
