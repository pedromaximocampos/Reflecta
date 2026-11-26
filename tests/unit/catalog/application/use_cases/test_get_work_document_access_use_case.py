from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.auth.public import UserId
from src.modules.catalog.application.use_cases.get_work_document_access import (
    GetWorkDocumentAccessInputDTO,
    GetWorkDocumentAccessUseCase,
)
from src.modules.catalog.domain.entities import WorkIngestion
from src.modules.catalog.domain.exceptions.work_exceptions import (
    WorkIngestionNotFoundError,
)
from src.modules.catalog.domain.value_objects import WorkDocumentLocation
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


INGESTION_ID = "01INGESTION000000000000000"
WORK_ID = "01WORK00000000000000000000"
ADMIN_ID = "01ADMIN0000000000000000000"


class FakeSQLUnitOfWork:
    def __init__(self) -> None:
        self.work_ingestion_repository = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


def make_ingestion() -> WorkIngestion:
    return WorkIngestion(
        id=WorkIngestionId(INGESTION_ID),
        work_id=WorkId(WORK_ID),
        requested_by=UserId(ADMIN_ID),
        document_location=WorkDocumentLocation(
            bucket="reflecta-works-dev",
            object_key=f"works/{WORK_ID}/source/{INGESTION_ID}.pdf",
        ),
        created_at=datetime(2026, 11, 25, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_creates_document_access_for_existing_ingestion() -> None:
    uow = FakeSQLUnitOfWork()
    ingestion = make_ingestion()
    uow.work_ingestion_repository.find_by_id.return_value = ingestion
    storage = AsyncMock()
    storage.create_read_url.return_value = "https://s3.example.test/signed-document"
    use_case = GetWorkDocumentAccessUseCase(
        uow,  # type: ignore[arg-type]
        storage,
        expires_in_seconds=300,
    )

    output = await use_case.execute(
        GetWorkDocumentAccessInputDTO(WorkIngestionId(INGESTION_ID))
    )

    storage.create_read_url.assert_awaited_once_with(
        location=ingestion.document_location
    )
    assert output.to_dict() == {
        "ingestion_id": INGESTION_ID,
        "url": "https://s3.example.test/signed-document",
        "expires_in_seconds": 300,
    }


@pytest.mark.asyncio
async def test_rejects_unknown_ingestion() -> None:
    uow = FakeSQLUnitOfWork()
    uow.work_ingestion_repository.find_by_id.return_value = None
    use_case = GetWorkDocumentAccessUseCase(
        uow,  # type: ignore[arg-type]
        AsyncMock(),
        expires_in_seconds=300,
    )

    with pytest.raises(WorkIngestionNotFoundError):
        await use_case.execute(
            GetWorkDocumentAccessInputDTO(WorkIngestionId(INGESTION_ID))
        )
