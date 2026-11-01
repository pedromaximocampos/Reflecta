from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.catalog.domain.entities.author import Author
from src.modules.catalog.domain.entities.work import Work
from src.modules.catalog.domain.value_objects.catalog_status import CatalogStatus
from src.modules.catalog.infrastructure.persistence.neo4j.mappers.author_mapper import AuthorMapper
from src.modules.catalog.infrastructure.persistence.neo4j.mappers.work_mapper import WorkMapper
from src.modules.catalog.infrastructure.persistence.neo4j.repositories.work_repository import WorkRepository
from src.modules.catalog.public.author_id import AuthorId
from src.modules.catalog.public.work_id import WorkId


@pytest.mark.asyncio
async def test_get_work_by_id_returns_mapped_work() -> None:
    created_at = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)
    work = Work(
        id=WorkId("01WORK0000000000000000000"),
        slug="meditacoes",
        title="Meditações",
        synopsis="Reflexões estoicas.",
        work_type="BOOK",
        language="pt-BR",
        status=CatalogStatus.INACTIVE,
        created_at=created_at,
    )
    result = AsyncMock()
    result.single.return_value = {"work": dict(WorkMapper().to_model(work))}
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = WorkRepository(transaction, WorkMapper(), AuthorMapper())

    found = await repository.get_work_by_id(work.id)

    assert found is not None
    assert found.id == work.id
    assert found.slug == work.slug
    assert found.title == work.title
    assert found.created_at == work.created_at
    transaction.run.assert_awaited_once()
    assert transaction.run.await_args.kwargs == {"work_id": work.id.value}


@pytest.mark.asyncio
async def test_get_work_with_author_by_id_maps_both_nodes() -> None:
    created_at = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)
    work = Work(
        id=WorkId("01WORK0000000000000000000"),
        slug="meditacoes",
        title="Meditações",
        synopsis="Reflexões estoicas.",
        work_type="BOOK",
        language="pt-BR",
        status=CatalogStatus.INACTIVE,
        created_at=created_at,
    )
    author = Author(
        id=AuthorId("01AUTHOR00000000000000000"),
        name="Marco Aurélio",
        normalized_name="marco-aurelio",
        description="Filósofo estoico.",
        created_at=created_at,
    )
    result = AsyncMock()
    result.single.return_value = {
        "work": dict(WorkMapper().to_model(work)),
        "author": dict(AuthorMapper().to_model(author)),
        "passage_count": 4,
        "active_passage_count": 1,
        "inactive_passage_count": 3,
    }
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = WorkRepository(transaction, WorkMapper(), AuthorMapper())

    found = await repository.get_work_with_author_by_id(work.id)

    assert found is not None
    assert found.work.id == work.id
    assert found.author.id == author.id
    assert found.passage_count == 4
    assert found.active_passage_count == 1
    assert found.inactive_passage_count == 3
    assert found.work.status is CatalogStatus.ACTIVE
    assert "[:WRITTEN_BY]" in transaction.run.await_args.args[0]
    assert transaction.run.await_args.kwargs == {"work_id": work.id.value}


@pytest.mark.asyncio
async def test_list_works_maps_nodes_in_repository_order() -> None:
    created_at = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)
    author = Author(
        id=AuthorId("01AUTHOR00000000000000000"),
        name="Marco Aurélio",
        normalized_name="marco-aurelio",
        description="Filósofo estoico.",
        created_at=created_at,
    )
    works = [
        Work(
            id=WorkId(f"01WORK000000000000000000{index}"),
            slug=f"work-{index}",
            title=f"Work {index}",
            synopsis="Reflexões.",
            work_type="BOOK",
            language="pt-BR",
            status=CatalogStatus.INACTIVE,
            created_at=created_at,
        )
        for index in range(2)
    ]
    result = AsyncMock()
    result.__aiter__.return_value = iter(
        {
            "work": dict(WorkMapper().to_model(work)),
            "author": dict(AuthorMapper().to_model(author)),
            "passage_count": index + 2,
            "active_passage_count": 1,
            "inactive_passage_count": index + 1,
        }
        for index, work in enumerate(works)
    )
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = WorkRepository(transaction, WorkMapper(), AuthorMapper())

    found = await repository.list_works()

    assert [record.work.id for record in found] == [work.id for work in works]
    assert all(record.author.id == author.id for record in found)
    assert [record.passage_count for record in found] == [2, 3]
    assert all(record.work.status is CatalogStatus.ACTIVE for record in found)
    query = transaction.run.await_args.args[0]
    assert "ORDER BY work.created_at DESC" in query


@pytest.mark.asyncio
async def test_update_work_replaces_properties_and_returns_mapped_work() -> None:
    updated_at = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)
    work = Work(
        id=WorkId("01WORK0000000000000000000"),
        slug="meditacoes",
        title="Meditações",
        synopsis="Reflexões estoicas.",
        work_type="BOOK",
        language="pt-BR",
        status=CatalogStatus.INACTIVE,
        created_at=datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc),
        cover_image_url="https://images.example.test/new-cover.jpg",
        updated_at=updated_at,
    )
    result = AsyncMock()
    result.single.return_value = {"work": dict(WorkMapper().to_model(work))}
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = WorkRepository(transaction, WorkMapper(), AuthorMapper())

    updated = await repository.update_work(work)

    assert updated.cover_image_url == work.cover_image_url
    assert updated.updated_at == updated_at
    assert transaction.run.await_args.kwargs["work_id"] == work.id.value
    assert transaction.run.await_args.kwargs["properties"]["cover_image_url"] == work.cover_image_url
    result.single.assert_awaited_once_with(strict=True)


@pytest.mark.asyncio
async def test_sync_status_derives_work_availability_from_active_passages() -> None:
    updated_at = datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)
    work = Work(
        id=WorkId("01WORK0000000000000000000"),
        slug="meditacoes",
        title="Meditações",
        synopsis="Reflexões estoicas.",
        work_type="BOOK",
        language="pt-BR",
        status=CatalogStatus.ACTIVE,
        created_at=datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc),
        updated_at=updated_at,
    )
    result = AsyncMock()
    result.single.return_value = {"work": dict(WorkMapper().to_model(work))}
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = WorkRepository(transaction, WorkMapper(), AuthorMapper())

    synchronized = await repository.sync_status_from_active_passages(
        work.id,
        updated_at,
    )

    assert synchronized.status is CatalogStatus.ACTIVE
    query = transaction.run.await_args.args[0]
    assert "passage:Passage {status: 'ACTIVE'}" in query
    assert "CASE WHEN count(passage) > 0 THEN 'ACTIVE' ELSE 'INACTIVE' END" in query
    assert transaction.run.await_args.kwargs == {
        "work_id": work.id.value,
        "updated_at": updated_at,
    }
    result.single.assert_awaited_once_with(strict=True)


@pytest.mark.asyncio
async def test_create_work_merges_author_and_creates_written_by_relation() -> None:
    created_at = datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)
    work = Work(
        id=WorkId("01WORK0000000000000000000"),
        slug="meditacoes",
        title="Meditações",
        synopsis="Reflexões estoicas.",
        work_type="BOOK",
        language="pt-BR",
        status=CatalogStatus.INACTIVE,
        created_at=created_at,
    )
    author = Author(
        id=AuthorId("01AUTHOR00000000000000000"),
        name="Marco Aurélio",
        normalized_name="marco-aurelio",
        description="Filósofo estoico.",
        created_at=created_at,
    )
    result = AsyncMock()
    result.single.return_value = {
        "work": dict(WorkMapper().to_model(work)),
        "author": dict(AuthorMapper().to_model(author)),
    }
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = WorkRepository(transaction, WorkMapper(), AuthorMapper())
    created_work, stored_author = await repository.create_work(work, author)
    query = transaction.run.await_args.args[0]
    assert "MERGE (stored_author:Author" in query
    assert "[:WRITTEN_BY]" in query
    assert created_work.id == work.id
    assert stored_author.id == author.id
    result.single.assert_awaited_once_with(strict=True)
