from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.auth.public import UserId
from src.modules.catalog.application.use_cases.reprocess_work_ingestion import (
    ReprocessWorkIngestionInputDTO,
    ReprocessWorkIngestionUseCase,
)
from src.modules.catalog.domain.entities import WorkIngestion
from src.modules.catalog.domain.exceptions.work_exceptions import (
    WorkIngestionNotFoundError,
    WorkIngestionNotReprocessableError,
)
from src.modules.catalog.domain.value_objects import (
    WorkDocumentLocation,
    WorkIngestionStatus,
)
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId


INGESTION_ID = "01INGESTION000000000000000"
WORK_ID = "01WORK00000000000000000000"
ADMIN_ID = "01ADMIN0000000000000000000"
NOW = datetime(2026, 11, 4, 12, tzinfo=timezone.utc)


class FixedClock:
    def now(self) -> datetime:
        return NOW


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


def make_ingestion(status: WorkIngestionStatus) -> WorkIngestion:
    return WorkIngestion(
        id=WorkIngestionId(INGESTION_ID),
        work_id=WorkId(WORK_ID),
        requested_by=UserId(ADMIN_ID),
        document_location=WorkDocumentLocation(
            bucket="reflecta-works-dev",
            object_key=f"works/{WORK_ID}/source/{INGESTION_ID}.pdf",
        ),
        created_at=NOW,
        status=status,
        attempts=3,
        started_at=NOW,
        finished_at=NOW if status is WorkIngestionStatus.FAILED else None,
        error_code=(
            "provider_connection_error"
            if status is WorkIngestionStatus.FAILED
            else None
        ),
        error_message=(
            "The provider was temporarily unavailable."
            if status is WorkIngestionStatus.FAILED
            else None
        ),
    )


def make_use_case(
    uow: FakeSQLUnitOfWork,
    outbox_service: AsyncMock,
) -> ReprocessWorkIngestionUseCase:
    return ReprocessWorkIngestionUseCase(
        catalog_sql_uow=uow,
        outbox_service=outbox_service,
        clock=FixedClock(),
    )


@pytest.mark.asyncio
async def test_requeues_failed_ingestion_and_creates_new_outbox_event() -> None:
    uow = FakeSQLUnitOfWork()
    ingestion = make_ingestion(WorkIngestionStatus.FAILED)
    uow.work_ingestion_repository.find_by_id_for_update.return_value = ingestion
    uow.work_ingestion_repository.update.side_effect = lambda entity: entity
    outbox_service = AsyncMock()

    output = await make_use_case(uow, outbox_service).execute(
        ReprocessWorkIngestionInputDTO(WorkIngestionId(INGESTION_ID))
    )

    event, repository = outbox_service.persist_event.await_args.args
    assert event.ingestion_id.value == INGESTION_ID
    assert event.work_id.value == WORK_ID
    assert event.document_location == ingestion.document_location
    assert event.occurred_at == NOW
    assert repository is uow.outbox_repository
    assert output.to_dict() == {
        "ingestion_id": INGESTION_ID,
        "work_id": WORK_ID,
        "status": "pending",
        "event_created": True,
    }
    assert ingestion.attempts == 3
    uow.commit.assert_awaited_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status",
    [WorkIngestionStatus.PENDING, WorkIngestionStatus.PROCESSING],
)
async def test_active_ingestion_returns_idempotently_without_new_event(
    status: WorkIngestionStatus,
) -> None:
    uow = FakeSQLUnitOfWork()
    ingestion = make_ingestion(status)
    uow.work_ingestion_repository.find_by_id_for_update.return_value = ingestion
    outbox_service = AsyncMock()

    output = await make_use_case(uow, outbox_service).execute(
        ReprocessWorkIngestionInputDTO(WorkIngestionId(INGESTION_ID))
    )

    assert output.status is status
    assert output.event_created is False
    outbox_service.persist_event.assert_not_awaited()
    uow.work_ingestion_repository.update.assert_not_awaited()
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_finished_ingestion() -> None:
    uow = FakeSQLUnitOfWork()
    uow.work_ingestion_repository.find_by_id_for_update.return_value = make_ingestion(
        WorkIngestionStatus.COMPLETED
    )

    with pytest.raises(WorkIngestionNotReprocessableError):
        await make_use_case(uow, AsyncMock()).execute(
            ReprocessWorkIngestionInputDTO(WorkIngestionId(INGESTION_ID))
        )


@pytest.mark.asyncio
async def test_rejects_unknown_ingestion() -> None:
    uow = FakeSQLUnitOfWork()
    uow.work_ingestion_repository.find_by_id_for_update.return_value = None

    with pytest.raises(WorkIngestionNotFoundError):
        await make_use_case(uow, AsyncMock()).execute(
            ReprocessWorkIngestionInputDTO(WorkIngestionId(INGESTION_ID))
        )
