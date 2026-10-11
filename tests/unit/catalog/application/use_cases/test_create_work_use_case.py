from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.catalog.application.use_cases.create_work.create_work_use_case import CreateWorkUseCase
from src.modules.catalog.application.use_cases.create_work.dto import CreateAuthorInputDTO, CreateWorkInputDTO
from src.modules.catalog.domain.exceptions.work_exceptions import WorkAlreadyExistsError
from src.modules.catalog.domain.value_objects.catalog_status import CatalogStatus
from src.shared.infrastructure.system.slug_generator import SlugGenerator


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 10, 5, 12, 0, tzinfo=timezone.utc)


class SequentialUlidGenerator:
    def __init__(self, *values: str) -> None:
        self._values = iter(values)

    def generate_ulid(self) -> str:
        return next(self._values)


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


def make_input() -> CreateWorkInputDTO:
    return CreateWorkInputDTO(
        title="Meditações",
        synopsis="Reflexões sobre ética, dever e vida interior.",
        work_type="BOOK",
        language="pt-BR",
        author=CreateAuthorInputDTO(
            name="Marco Aurélio",
            description="Imperador romano e filósofo estoico.",
        ),
    )


def make_use_case(uow: FakeCatalogUnitOfWork) -> CreateWorkUseCase:
    return CreateWorkUseCase(
        catalog_graph_uow=uow,
        ulid_generator=SequentialUlidGenerator(
            "01AUTHOR00000000000000000",
            "01WORK0000000000000000000",
        ),
        clock=FixedClock(),
        slug_generator=SlugGenerator(),
    )


@pytest.mark.asyncio
async def test_create_work_persists_inactive_work_with_author_relation() -> None:
    uow = FakeCatalogUnitOfWork()
    uow.work_repository.get_work_by_slug.return_value = None
    uow.work_repository.create_work.side_effect = lambda work, author: (work, author)
    output = await make_use_case(uow).execute(make_input())
    work, author = uow.work_repository.create_work.await_args.args
    assert work.slug == "meditacoes"
    assert work.status is CatalogStatus.INACTIVE
    assert author.normalized_name == "marco-aurelio"
    assert output.author.id == author.id
    uow.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_create_work_rejects_existing_slug_and_rolls_back() -> None:
    uow = FakeCatalogUnitOfWork()
    uow.work_repository.get_work_by_slug.return_value = object()
    with pytest.raises(WorkAlreadyExistsError):
        await make_use_case(uow).execute(make_input())
    uow.work_repository.create_work.assert_not_awaited()
    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once_with()
