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
