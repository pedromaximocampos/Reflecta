from datetime import UTC, datetime

import pytest

from src.modules.ai_processing.application.use_cases.list_work_ingestions import (
    ListWorkIngestionsUseCase,
)
from src.modules.ai_processing.domain.value_objects import WorkIngestionChunkStatus
from src.modules.catalog.public import WorkIngestionSummary
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


INGESTION_ONE = WorkIngestionId("01ARZ3NDEKTSV4RRFFQ69G5FAA")
INGESTION_TWO = WorkIngestionId("01ARZ3NDEKTSV4RRFFQ69G5FAB")
WORK_ID = WorkId("01ARZ3NDEKTSV4RRFFQ69G5FAC")
NOW = datetime(2026, 10, 31, 18, tzinfo=UTC)


class _Catalog:
    def __init__(self) -> None:
        self.limit = None

    async def list_recent(self, *, limit):
        self.limit = limit
        return (
            WorkIngestionSummary(
                ingestion_id=INGESTION_ONE,
                work_id=WORK_ID,
                status="processing",
                attempts=2,
                created_at=NOW,
                started_at=NOW,
                finished_at=None,
                error_code=None,
            ),
            WorkIngestionSummary(
                ingestion_id=INGESTION_TWO,
                work_id=WORK_ID,
                status="pending",
                attempts=0,
                created_at=NOW,
                started_at=None,
                finished_at=None,
                error_code=None,
            ),
        )


class _Chunks:
    def __init__(self) -> None:
        self.ids = None

    async def count_many_by_status(self, ingestion_ids):
        self.ids = ingestion_ids
        return {
            INGESTION_ONE: {
                WorkIngestionChunkStatus.COMPLETED: 3,
                WorkIngestionChunkStatus.PROCESSING: 1,
                WorkIngestionChunkStatus.PENDING: 2,
            }
        }


class _Uow:
    def __init__(self, chunks) -> None:
        self.work_ingestion_chunk_repository = chunks

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None


class _Failures:
    def __init__(self) -> None:
        self.ids = None

    async def latest_active_for_ingestions(self, ingestion_ids):
        self.ids = ingestion_ids
        return {
            INGESTION_TWO.value: {
                "source": "outbox",
                "id": "01ARZ3NDEKTSV4RRFFQ69G5FAD",
                "code": "aws_credentials_unavailable",
                "message": "As credenciais AWS do publicador estão indisponíveis ou expiraram.",
                "occurred_at": NOW.isoformat(),
            }
        }


@pytest.mark.asyncio
async def test_lists_ingestions_with_batch_chunk_progress() -> None:
    catalog = _Catalog()
    chunks = _Chunks()
    failures = _Failures()
    result = await ListWorkIngestionsUseCase(
        catalog,
        _Uow(chunks),
        failures,
    ).execute(limit=50)

    assert catalog.limit == 50
    assert chunks.ids == (INGESTION_ONE, INGESTION_TWO)
    assert failures.ids == (INGESTION_ONE, INGESTION_TWO)
    assert result.to_dict() == {
        "ingestions": [
            {
                "ingestion_id": INGESTION_ONE.value,
                "work_id": WORK_ID.value,
                "status": "processing",
                "attempts": 2,
                "created_at": NOW.isoformat(),
                "started_at": NOW.isoformat(),
                "finished_at": None,
                "error_code": None,
                "progress": {
                    "total": 6,
                    "pending": 2,
                    "processing": 1,
                    "completed": 3,
                    "failed": 0,
                    "percentage": 50,
                },
                "failure": None,
            },
            {
                "ingestion_id": INGESTION_TWO.value,
                "work_id": WORK_ID.value,
                "status": "pending",
                "attempts": 0,
                "created_at": NOW.isoformat(),
                "started_at": None,
                "finished_at": None,
                "error_code": None,
                "progress": {
                    "total": 0,
                    "pending": 0,
                    "processing": 0,
                    "completed": 0,
                    "failed": 0,
                    "percentage": None,
                },
                "failure": {
                    "source": "outbox",
                    "failure_id": "01ARZ3NDEKTSV4RRFFQ69G5FAD",
                    "code": "aws_credentials_unavailable",
                    "message": "As credenciais AWS do publicador estão indisponíveis ou expiraram.",
                    "occurred_at": NOW.isoformat(),
                },
            },
        ]
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("limit", [0, 101])
async def test_rejects_limits_outside_the_public_contract(limit: int) -> None:
    with pytest.raises(ValueError, match="limit"):
        await ListWorkIngestionsUseCase(
            _Catalog(),
            _Uow(_Chunks()),
            _Failures(),
        ).execute(limit=limit)
