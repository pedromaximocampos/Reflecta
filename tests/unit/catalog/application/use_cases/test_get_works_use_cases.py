from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import AsyncMock

import pytest

from src.modules.catalog.application.use_cases.get_works import (
    GetAllWorksUseCase,
    GetWorkByIdUseCase,
)
from src.modules.catalog.application.use_cases.update_work_cover import (
    RemoveWorkCoverInputDTO,
    RemoveWorkCoverUseCase,
    ReplaceWorkCoverInputDTO,
    ReplaceWorkCoverUseCase,
)
from src.modules.catalog.application.dto import (
    ProcessedWorkCoverDTO,
    StoredWorkCoverDTO,
)
from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.domain.exceptions.work_exceptions import WorkNotFoundError
from src.modules.catalog.domain.ports.repositories.iwork_repository import (
    WorkCatalogRecord,
)
from src.modules.catalog.domain.value_objects.catalog_status import CatalogStatus
from src.modules.catalog.public.author_id import AuthorId
from src.modules.catalog.public.work_id import WorkId


class FakeCatalogUnitOfWork:
    def __init__(self) -> None:
        self.work_repository = AsyncMock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()


class FixedClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class FixedUlidGenerator:
    def generate_ulid(self) -> str:
        return "01COVER0000000000000000000"


def cover_storage() -> AsyncMock:
    storage = AsyncMock()
    storage.create_read_url.return_value = "https://signed.example.test/cover.webp"
    storage.upload.return_value = StoredWorkCoverDTO(
        object_key="works/01WORK0000000000000000000/cover/01COVER0000000000000000000.webp",
        content_type="image/webp",
        size_bytes=4,
    )
    return storage


def make_work_with_author(
    work_id: str = "01WORK0000000000000000000",
) -> WorkCatalogRecord:
    created_at = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)
    return WorkCatalogRecord(
        work=Work(
            id=WorkId(work_id),
            slug="meditacoes",
            title="Meditações",
            synopsis="Reflexões estoicas.",
            work_type="BOOK",
            language="pt-BR",
            status=CatalogStatus.INACTIVE,
            created_at=created_at,
            cover_image_url="https://images.example.test/meditacoes.jpg",
        ),
        author=Author(
            id=AuthorId("01AUTHOR00000000000000000"),
            name="Marco Aurélio",
            normalized_name="marco-aurelio",
            description="Filósofo estoico.",
            created_at=created_at,
        ),
        passage_count=4,
        active_passage_count=1,
        inactive_passage_count=3,
    )


@pytest.mark.asyncio
async def test_get_work_by_id_returns_work_with_author_without_committing() -> None:
    uow = FakeCatalogUnitOfWork()
    record = make_work_with_author()
    uow.work_repository.get_work_with_author_by_id.return_value = record

    output = await GetWorkByIdUseCase(uow, cover_storage()).execute(record.work.id)

    assert output.to_dict()["id"] == record.work.id.value
    assert output.to_dict()["author"]["name"] == record.author.name
    assert output.to_dict()["cover_image_url"] == record.work.cover_image_url
    assert output.to_dict()["passage_counts"] == {
        "total": 4,
        "active": 1,
        "inactive": 3,
    }
    uow.work_repository.get_work_with_author_by_id.assert_awaited_once_with(
        record.work.id
    )
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_work_by_id_raises_not_found_and_rolls_back() -> None:
    uow = FakeCatalogUnitOfWork()
    work_id = WorkId("01MISSING000000000000000000")
    uow.work_repository.get_work_with_author_by_id.return_value = None

    with pytest.raises(WorkNotFoundError) as raised:
        await GetWorkByIdUseCase(uow, cover_storage()).execute(work_id)

    assert raised.value.status_code == 404
    uow.rollback.assert_awaited_once_with()
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_all_works_returns_work_and_author_data() -> None:
    uow = FakeCatalogUnitOfWork()
    first = make_work_with_author()
    second = make_work_with_author("01WORK0000000000000000001")
    second.work.title = "Manual de Epicteto"
    second.work.slug = "manual-de-epicteto"
    uow.work_repository.list_works.return_value = [first, second]

    output = await GetAllWorksUseCase(uow, cover_storage()).execute()

    payload = output.to_dict()
    assert [work["id"] for work in payload["works"]] == [
        first.work.id.value,
        second.work.id.value,
    ]
    assert payload["works"][0]["author"]["name"] == first.author.name
    uow.work_repository.list_works.assert_awaited_once_with()
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_all_works_allows_empty_catalog() -> None:
    uow = FakeCatalogUnitOfWork()
    uow.work_repository.list_works.return_value = []

    output = await GetAllWorksUseCase(uow, cover_storage()).execute()

    assert output.to_dict() == {"works": []}


@pytest.mark.asyncio
async def test_replace_work_cover_uploads_key_commits_and_deletes_previous() -> None:
    uow = FakeCatalogUnitOfWork()
    record = make_work_with_author()
    record.work.cover_object_key = "works/old/cover/old.webp"
    updated_at = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)
    uow.work_repository.get_work_by_id.return_value = record.work
    uow.work_repository.get_work_with_author_by_id.return_value = record
    uow.work_repository.update_work.side_effect = lambda work: work
    processor = AsyncMock()
    processor.process.return_value = ProcessedWorkCoverDTO(
        content=BytesIO(b"webp"),
        content_type="image/webp",
        size_bytes=4,
        extension="webp",
    )
    storage = cover_storage()

    output = await ReplaceWorkCoverUseCase(
        uow,
        processor,
        storage,
        FixedUlidGenerator(),
        FixedClock(updated_at),
    ).execute(
        ReplaceWorkCoverInputDTO(
            work_id=record.work.id,
            content=BytesIO(b"input"),
            content_type="image/png",
            size_bytes=5,
        )
    )

    assert output.cover_image_url == "https://signed.example.test/cover.webp"
    assert record.work.cover_object_key.endswith(".webp")
    assert record.work.cover_image_url is None
    assert output.updated_at == updated_at
    uow.work_repository.update_work.assert_awaited_once_with(record.work)
    uow.commit.assert_awaited_once_with()
    storage.delete.assert_awaited_once_with(
        object_key="works/old/cover/old.webp"
    )


@pytest.mark.asyncio
async def test_remove_work_cover_clears_key_and_deletes_object() -> None:
    uow = FakeCatalogUnitOfWork()
    record = make_work_with_author()
    record.work.cover_object_key = "works/old/cover/old.webp"
    uow.work_repository.get_work_with_author_by_id.return_value = record
    uow.work_repository.update_work.side_effect = lambda work: work
    storage = cover_storage()

    output = await RemoveWorkCoverUseCase(
        uow,
        storage,
        FixedClock(datetime(2026, 10, 6, tzinfo=timezone.utc)),
    ).execute(
        RemoveWorkCoverInputDTO(
            work_id=record.work.id,
        )
    )

    assert output.cover_image_url is None
    assert record.work.cover_object_key is None
    storage.delete.assert_awaited_once_with(
        object_key="works/old/cover/old.webp"
    )
