from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.catalog.application.use_cases.get_themes.get_all_themes_use_case import (
    GetAllThemesUseCase,
)
from src.modules.catalog.application.use_cases.get_themes.get_theme_by_id_use_case import (
    GetThemeByIdUseCase,
)
from src.modules.catalog.domain.entities.theme import Theme
from src.modules.catalog.domain.exceptions.theme_exceptions import ThemeNotFoundError
from src.modules.catalog.public.theme_id import ThemeId


class FakeCatalogUnitOfWork:
    def __init__(self) -> None:
        self.theme_repository = AsyncMock()
        self.commit = AsyncMock()
        self.rollback = AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()


def make_theme(identifier: str = "01THEME0000000000000000000") -> Theme:
    return Theme(
        id=ThemeId(identifier),
        slug="autoconhecimento",
        label="Autoconhecimento",
        description="Reflexões relacionadas ao conhecimento de si.",
        is_active=True,
        created_at=datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_get_theme_by_id_returns_mapped_theme_without_committing() -> None:
    uow = FakeCatalogUnitOfWork()
    theme = make_theme()
    uow.theme_repository.get_theme_by_id.return_value = theme

    output = await GetThemeByIdUseCase(uow).execute(theme.id)

    assert output.to_dict() == {
        "id": theme.id.value,
        "slug": theme.slug,
        "label": theme.label,
        "description": theme.description,
        "is_active": True,
        "created_at": theme.created_at.isoformat(),
        "updated_at": None,
    }
    uow.theme_repository.get_theme_by_id.assert_awaited_once_with(theme.id)
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_theme_by_id_raises_not_found_and_rolls_back() -> None:
    uow = FakeCatalogUnitOfWork()
    theme_id = ThemeId("01MISSING00000000000000000")
    uow.theme_repository.get_theme_by_id.return_value = None

    with pytest.raises(ThemeNotFoundError) as raised:
        await GetThemeByIdUseCase(uow).execute(theme_id)

    assert raised.value.status_code == 404
    uow.commit.assert_not_awaited()
    uow.rollback.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_all_themes_returns_mapped_ordered_result() -> None:
    uow = FakeCatalogUnitOfWork()
    first = make_theme("01THEME0000000000000000000")
    second = make_theme("01THEME0000000000000000001")
    second.label = "Bem-estar"
    second.slug = "bem-estar"
    uow.theme_repository.list_themes.return_value = [first, second]

    output = await GetAllThemesUseCase(uow).execute()

    assert [theme["id"] for theme in output.to_dict()["themes"]] == [
        first.id.value,
        second.id.value,
    ]
    uow.theme_repository.list_themes.assert_awaited_once_with()
    uow.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_all_themes_allows_empty_catalog() -> None:
    uow = FakeCatalogUnitOfWork()
    uow.theme_repository.list_themes.return_value = []

    output = await GetAllThemesUseCase(uow).execute()

    assert output.to_dict() == {"themes": []}
