from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.catalog.application.use_cases.create_themes.create_themes_use_case import (
    CreateThemesUseCase,
)
from src.modules.catalog.application.use_cases.create_themes.dto import (
    CreateThemeInputDTO,
    CreateThemesInputDTO,
)
from src.modules.catalog.domain.exceptions.theme_exceptions import (
    EmptyThemeBatchError,
    InvalidThemeSlugError,
    ThemeAlreadyExistsError,
)
from src.shared.infrastructure.system.slug_generator import SlugGenerator


class FixedClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


class SequentialUlidGenerator:
    def __init__(self, *values: str) -> None:
        self._values = iter(values)

    def generate_ulid(self) -> str:
        return next(self._values)


class FakeCatalogUnitOfWork:
    def __init__(self) -> None:
        self.theme_repository = AsyncMock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        self.enter_count = 0

    async def __aenter__(self):
        self.enter_count += 1
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()


def make_use_case(uow: FakeCatalogUnitOfWork) -> CreateThemesUseCase:
    return CreateThemesUseCase(
        catalog_graph_uow=uow,
        ulid_generator=SequentialUlidGenerator(
            "01THEME0000000000000000000",
            "01THEME0000000000000000001",
        ),
        clock=FixedClock(datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)),
        slug_generator=SlugGenerator(),
    )


@pytest.mark.asyncio
async def test_execute_persists_batch_and_commits_once() -> None:
    uow = FakeCatalogUnitOfWork()
    uow.theme_repository.get_theme_by_slug.return_value = None
    uow.theme_repository.create_many_themes.side_effect = lambda themes: themes
    use_case = make_use_case(uow)
    input_dto = CreateThemesInputDTO(
        themes=[
            CreateThemeInputDTO(
                label="Saúde Mental",
                description="Reflexões sobre saúde mental.",
            ),
            CreateThemeInputDTO(
                label="Autoconhecimento",
                description="Reflexões relacionadas ao conhecimento de si.",
                is_active=False,
            ),
        ]
    )

    output = await use_case.execute(input_dto)

    persisted = uow.theme_repository.create_many_themes.await_args.args[0]
    assert [theme.slug for theme in persisted] == [
        "saude-mental",
        "autoconhecimento",
    ]
    assert persisted[0].created_at == persisted[1].created_at
    uow.commit.assert_awaited_once_with()
    assert uow.enter_count == 1
    assert uow.theme_repository.get_theme_by_slug.await_count == 2
    assert output.to_dict()["themes"][0]["id"] == "01THEME0000000000000000000"
    assert output.to_dict()["themes"][0]["slug"] == "saude-mental"


@pytest.mark.asyncio
async def test_execute_rejects_duplicate_normalized_slugs_before_opening_uow() -> None:
    uow = FakeCatalogUnitOfWork()
    use_case = make_use_case(uow)
    input_dto = CreateThemesInputDTO(
        themes=[
            CreateThemeInputDTO(label="Saúde Mental", description="Primeira."),
            CreateThemeInputDTO(label="saude mental", description="Segunda."),
        ]
    )

    with pytest.raises(ThemeAlreadyExistsError) as raised:
        await use_case.execute(input_dto)

    assert raised.value.status_code == 409
    assert uow.enter_count == 0
    uow.theme_repository.create_many_themes.assert_not_awaited()
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_rejects_label_that_produces_empty_slug() -> None:
    uow = FakeCatalogUnitOfWork()
    use_case = make_use_case(uow)

    with pytest.raises(InvalidThemeSlugError):
        await use_case.execute(
            CreateThemesInputDTO(
                themes=[CreateThemeInputDTO(label="!!!", description="Inválido.")]
            )
        )

    assert uow.enter_count == 0
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_rejects_empty_batch_before_opening_uow() -> None:
    uow = FakeCatalogUnitOfWork()
    use_case = make_use_case(uow)

    with pytest.raises(EmptyThemeBatchError):
        await use_case.execute(CreateThemesInputDTO(themes=[]))

    assert uow.enter_count == 0
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_execute_does_not_commit_when_repository_fails() -> None:
    uow = FakeCatalogUnitOfWork()
    uow.theme_repository.get_theme_by_slug.return_value = None
    uow.theme_repository.create_many_themes.side_effect = ThemeAlreadyExistsError(
        "saude-mental"
    )
    use_case = make_use_case(uow)

    with pytest.raises(ThemeAlreadyExistsError):
        await use_case.execute(
            CreateThemesInputDTO(
                themes=[
                    CreateThemeInputDTO(
                        label="Saúde Mental",
                        description="Tema já existente.",
                    )
                ]
            )
        )

    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_execute_rejects_slug_already_stored_in_neo4j() -> None:
    uow = FakeCatalogUnitOfWork()
    uow.theme_repository.get_theme_by_slug.return_value = object()
    use_case = make_use_case(uow)

    with pytest.raises(ThemeAlreadyExistsError):
        await use_case.execute(
            CreateThemesInputDTO(
                themes=[
                    CreateThemeInputDTO(
                        label="Saúde Mental",
                        description="Tema já existente.",
                    )
                ]
            )
        )

    uow.theme_repository.create_many_themes.assert_not_awaited()
    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once_with()
