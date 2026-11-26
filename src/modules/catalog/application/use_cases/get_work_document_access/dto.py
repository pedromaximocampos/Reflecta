from dataclasses import dataclass

from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


@dataclass(frozen=True, slots=True)
class GetWorkDocumentAccessInputDTO:
    ingestion_id: WorkIngestionId


@dataclass(frozen=True, slots=True)
class GetWorkDocumentAccessOutputDTO:
    ingestion_id: WorkIngestionId
    url: str
    expires_in_seconds: int

    def to_dict(self) -> dict[str, str | int]:
        return {
            "ingestion_id": self.ingestion_id.value,
            "url": self.url,
            "expires_in_seconds": self.expires_in_seconds,
        }
