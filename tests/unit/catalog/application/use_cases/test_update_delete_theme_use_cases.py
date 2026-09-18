from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.catalog.application.use_cases.delete_themes.delete_theme_by_id_use_case import (
    DeleteThemeByIdUseCase,
)
from src.modules.catalog.application.use_cases.update_themes.dto import (
    UpdateThemeInputDTO,
)
from src.modules.catalog.application.use_cases.update_themes.update_theme_use_case import (
    UpdateThemeUseCase,
)
from src.modules.catalog.domain.entities.theme import Theme
from src.modules.catalog.domain.exceptions.theme_exceptions import (
    EmptyThemeUpdateError,
    ThemeNotFoundError,
)
from src.modules.catalog.public.theme_id import ThemeId


class FixedClock:
    def __init__(self, now: datetime) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now


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


def make_theme() -> Theme:
    return Theme(
        id=ThemeId("01THEME0000000000000000000"),
        slug="autoconhecimento",
        label="Autoconhecimento",
        description="Reflexões relacionadas ao conhecimento de si.",
        is_active=True,
        created_at=datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc),
    )


def make_update_use_case(uow: FakeCatalogUnitOfWork) -> UpdateThemeUseCase:
    return UpdateThemeUseCase(
        catalog_graph_uow=uow,
        clock=FixedClock(datetime(2026, 9, 18, 14, 0, tzinfo=timezone.utc)),
    )


@pytest.mark.asyncio
async def test_update_theme_changes_fields_preserves_slug_and_commits() -> None:
    uow = FakeCatalogUnitOfWork()
    theme = make_theme()
    uow.theme_repository.get_theme_by_id.return_value = theme
    uow.theme_repository.update_theme.side_effect = lambda entity: entity

    output = await make_update_use_case(uow).execute(
        UpdateThemeInputDTO(
            theme_id=theme.id,
            label="Consciência de si",
            description="Descrição atualizada.",
            is_active=False,
        )
    )

    persisted = uow.theme_repository.update_theme.await_args.args[0]
    assert persisted.label == "Consciência de si"
    assert persisted.description == "Descrição atualizada."
    assert persisted.is_active is False
    assert persisted.slug == "autoconhecimento"
    assert persisted.updated_at == datetime(
        2026, 9, 18, 14, 0, tzinfo=timezone.utc
    )
    assert output.slug == "autoconhecimento"
    uow.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_update_theme_can_activate_theme_without_other_changes() -> None:
    uow = FakeCatalogUnitOfWork()
    theme = make_theme()
    theme.is_active = False
    uow.theme_repository.get_theme_by_id.return_value = theme
    uow.theme_repository.update_theme.side_effect = lambda entity: entity

    output = await make_update_use_case(uow).execute(
        UpdateThemeInputDTO(theme_id=theme.id, is_active=True)
    )

    assert output.is_active is True
    assert output.updated_at == datetime(2026, 9, 18, 14, 0, tzinfo=timezone.utc)
    uow.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_update_theme_rejects_empty_update_before_opening_uow() -> None:
    uow = FakeCatalogUnitOfWork()

    with pytest.raises(EmptyThemeUpdateError) as raised:
        await make_update_use_case(uow).execute(
            UpdateThemeInputDTO(theme_id=make_theme().id)
        )

    assert raised.value.status_code == 400
    assert uow.enter_count == 0
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_theme_raises_not_found_without_committing() -> None:
    uow = FakeCatalogUnitOfWork()
    theme_id = make_theme().id
    uow.theme_repository.get_theme_by_id.return_value = None

    with pytest.raises(ThemeNotFoundError):
        await make_update_use_case(uow).execute(
            UpdateThemeInputDTO(theme_id=theme_id, label="Novo nome")
        )

    uow.theme_repository.update_theme.assert_not_awaited()
    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_update_theme_rolls_back_when_repository_fails() -> None:
    uow = FakeCatalogUnitOfWork()
    theme = make_theme()
    uow.theme_repository.get_theme_by_id.return_value = theme
    uow.theme_repository.update_theme.side_effect = RuntimeError("Neo4j unavailable")

    with pytest.raises(RuntimeError, match="Neo4j unavailable"):
        await make_update_use_case(uow).execute(
            UpdateThemeInputDTO(theme_id=theme.id, label="Novo nome")
        )

    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_delete_theme_deletes_existing_theme_and_commits() -> None:
    uow = FakeCatalogUnitOfWork()
    theme = make_theme()
    uow.theme_repository.get_theme_by_id.return_value = theme

    await DeleteThemeByIdUseCase(uow).execute(theme.id)

    uow.theme_repository.delete_theme.assert_awaited_once_with(theme.id)
    uow.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_delete_theme_raises_not_found_without_committing() -> None:
    uow = FakeCatalogUnitOfWork()
    theme_id = make_theme().id
    uow.theme_repository.get_theme_by_id.return_value = None

    with pytest.raises(ThemeNotFoundError) as raised:
        await DeleteThemeByIdUseCase(uow).execute(theme_id)

    assert raised.value.status_code == 404
    uow.theme_repository.delete_theme.assert_not_awaited()
    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once_with()
