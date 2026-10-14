from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import AsyncMock

import pytest

from src.modules.auth.public import UserId
from src.modules.catalog.application.dto.stored_work_document import (
    StoredWorkDocumentDTO,
)
from src.modules.catalog.application.use_cases.request_work_ingestion import (
    RequestWorkIngestionInputDTO,
    RequestWorkIngestionUseCase,
)
from src.modules.catalog.domain.exceptions.work_exceptions import (
    InvalidWorkDocumentError,
    WorkNotFoundError,
)
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)
from src.modules.catalog.public.work_id import WorkId


WORK_ID = "01WORK0000000000000000000"
INGESTION_ID = "01INGESTION000000000000000"
ADMIN_ID = "01ADMIN0000000000000000000"
NOW = datetime(2026, 10, 8, 12, 0, tzinfo=timezone.utc)
PDF_CONTENT = b"%PDF-1.7\nreflecta"


class FixedClock:
    def now(self) -> datetime:
        return NOW


class FixedUlidGenerator:
    def generate_ulid(self) -> str:
        return INGESTION_ID


class FakeGraphUnitOfWork:
    def __init__(self) -> None:
        self.work_repository = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None


class FakeSQLUnitOfWork:
    def __init__(self) -> None:
        self.work_ingestion_repository = AsyncMock()
        self.outbox_repository = AsyncMock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()


def make_input(content: bytes = PDF_CONTENT) -> RequestWorkIngestionInputDTO:
    return RequestWorkIngestionInputDTO(
        work_id=WorkId(WORK_ID),
        requested_by=UserId(ADMIN_ID),
        filename="meditacoes.pdf",
        content_type="application/pdf",
        size_bytes=len(content),
        content=BytesIO(content),
    )


def make_use_case(
    graph_uow: FakeGraphUnitOfWork,
    sql_uow: FakeSQLUnitOfWork,
    storage: AsyncMock,
    outbox_service: AsyncMock,
) -> RequestWorkIngestionUseCase:
    return RequestWorkIngestionUseCase(
        catalog_graph_uow=graph_uow,
        catalog_sql_uow=sql_uow,
        work_document_storage=storage,
        outbox_service=outbox_service,
        ulid_generator=FixedUlidGenerator(),
        clock=FixedClock(),
    )


def configure_successful_storage(storage: AsyncMock) -> WorkDocumentLocation:
    location = WorkDocumentLocation(
        bucket="reflecta-works-dev",
        object_key=f"works/{WORK_ID}/source/{INGESTION_ID}.pdf",
    )
    storage.upload.return_value = StoredWorkDocumentDTO(
        location=location,
        content_type="application/pdf",
        size_bytes=len(PDF_CONTENT),
        etag="etag",
    )
    return location


@pytest.mark.asyncio
async def test_requests_ingestion_and_persists_event_atomically() -> None:
    graph_uow = FakeGraphUnitOfWork()
    graph_uow.work_repository.get_work_by_id.return_value = object()
    sql_uow = FakeSQLUnitOfWork()
    sql_uow.work_ingestion_repository.create.side_effect = lambda ingestion: ingestion
    storage = AsyncMock()
    location = configure_successful_storage(storage)
    outbox_service = AsyncMock()
    ingestion_input = make_input()

    output = await make_use_case(
        graph_uow,
        sql_uow,
        storage,
        outbox_service,
    ).execute(ingestion_input)

    graph_uow.work_repository.get_work_by_id.assert_awaited_once_with(
        ingestion_input.work_id
    )
    storage.upload.assert_awaited_once_with(
        object_key=location.object_key,
        content=ingestion_input.content,
        content_type="application/pdf",
        size_bytes=len(PDF_CONTENT),
    )
    created_ingestion = sql_uow.work_ingestion_repository.create.await_args.args[0]
    event, outbox_repository = outbox_service.persist_event.await_args.args
    assert created_ingestion.document_location == location
    assert created_ingestion.created_at == NOW
    assert event.ingestion_id == created_ingestion.id
    assert event.document_location == location
    assert outbox_repository is sql_uow.outbox_repository
    sql_uow.commit.assert_awaited_once_with()
    storage.delete.assert_not_awaited()
    assert output.to_dict() == {
        "ingestion_id": INGESTION_ID,
        "work_id": WORK_ID,
        "status": "pending",
    }


@pytest.mark.asyncio
async def test_rejects_ingestion_when_work_does_not_exist() -> None:
    graph_uow = FakeGraphUnitOfWork()
    graph_uow.work_repository.get_work_by_id.return_value = None
    sql_uow = FakeSQLUnitOfWork()
    storage = AsyncMock()
    outbox_service = AsyncMock()

    with pytest.raises(WorkNotFoundError):
        await make_use_case(
            graph_uow,
            sql_uow,
            storage,
            outbox_service,
        ).execute(make_input())

    storage.upload.assert_not_awaited()
    sql_uow.work_ingestion_repository.create.assert_not_awaited()
    outbox_service.persist_event.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_spoofed_pdf_before_accessing_persistence() -> None:
    graph_uow = FakeGraphUnitOfWork()
    sql_uow = FakeSQLUnitOfWork()
    storage = AsyncMock()
    outbox_service = AsyncMock()

    with pytest.raises(InvalidWorkDocumentError):
        await make_use_case(
            graph_uow,
            sql_uow,
            storage,
            outbox_service,
        ).execute(make_input(b"not-a-pdf"))

    graph_uow.work_repository.get_work_by_id.assert_not_awaited()
    storage.upload.assert_not_awaited()


@pytest.mark.asyncio
async def test_deletes_uploaded_document_when_outbox_transaction_fails() -> None:
    graph_uow = FakeGraphUnitOfWork()
    graph_uow.work_repository.get_work_by_id.return_value = object()
    sql_uow = FakeSQLUnitOfWork()
    sql_uow.work_ingestion_repository.create.side_effect = lambda ingestion: ingestion
    storage = AsyncMock()
    location = configure_successful_storage(storage)
    outbox_service = AsyncMock()
    outbox_service.persist_event.side_effect = RuntimeError("outbox failure")

    with pytest.raises(RuntimeError, match="outbox failure"):
        await make_use_case(
            graph_uow,
            sql_uow,
            storage,
            outbox_service,
        ).execute(make_input())

    sql_uow.rollback.assert_awaited_once_with()
    sql_uow.commit.assert_not_awaited()
    storage.delete.assert_awaited_once_with(location=location)
