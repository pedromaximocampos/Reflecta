from dataclasses import asdict
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from neo4j.exceptions import ConstraintError

from src.modules.catalog.domain.entities.theme import Theme
from src.modules.catalog.domain.exceptions.theme_exceptions import ThemeAlreadyExistsError
from src.modules.catalog.infrastructure.persistence.neo4j.mappers.theme_mapper import (
    ThemeMapper,
)
from src.modules.catalog.infrastructure.persistence.neo4j.repositories.theme_repository import (
    ThemeRepository,
)
from src.modules.catalog.public.theme_id import ThemeId


def make_theme(identifier: str = "01THEME0000000000000000000") -> Theme:
    return Theme(
        id=ThemeId(identifier),
        slug="autoconhecimento",
        label="Autoconhecimento",
        description="Reflexões relacionadas ao conhecimento de si.",
        is_active=True,
        created_at=datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc),
    )


def node_from(theme: Theme) -> dict:
    return dict(ThemeMapper().to_model(theme))


def assert_same_theme(actual: Theme, expected: Theme) -> None:
    assert asdict(actual) == asdict(expected)


def make_result(*records: dict) -> AsyncMock:
    result = AsyncMock()
    result.single.return_value = records[0] if records else None
    result.__aiter__.return_value = iter(records)
    return result


@pytest.mark.asyncio
async def test_get_theme_by_id_maps_node_to_domain_entity() -> None:
    theme = make_theme()
    result = make_result({"theme": node_from(theme)})
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = ThemeRepository(transaction, ThemeMapper())

    found = await repository.get_theme_by_id(theme.id)

    assert found is not None
    assert_same_theme(found, theme)
    assert transaction.run.await_args.kwargs["theme_id"] == theme.id.value
    result.single.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_theme_by_id_returns_none_when_node_does_not_exist() -> None:
    transaction = AsyncMock()
    transaction.run.return_value = make_result()
    repository = ThemeRepository(transaction, ThemeMapper())

    found = await repository.get_theme_by_id(ThemeId("missing"))

    assert found is None


@pytest.mark.asyncio
async def test_get_theme_by_slug_maps_node_to_domain_entity() -> None:
    theme = make_theme()
    result = make_result({"theme": node_from(theme)})
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = ThemeRepository(transaction, ThemeMapper())

    found = await repository.get_theme_by_slug(theme.slug)

    assert found is not None
    assert_same_theme(found, theme)
    assert transaction.run.await_args.kwargs["slug"] == theme.slug


@pytest.mark.asyncio
async def test_get_theme_by_slug_returns_none_when_node_does_not_exist() -> None:
    transaction = AsyncMock()
    transaction.run.return_value = make_result()
    repository = ThemeRepository(transaction, ThemeMapper())

    found = await repository.get_theme_by_slug("missing")

    assert found is None


@pytest.mark.asyncio
async def test_create_theme_persists_all_properties_and_returns_entity() -> None:
    theme = make_theme()
    result = make_result({"theme": node_from(theme)})
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = ThemeRepository(transaction, ThemeMapper())

    created = await repository.create_theme(theme)

    assert_same_theme(created, theme)
    assert transaction.run.await_args.kwargs["properties"] == node_from(theme)
    result.single.assert_awaited_once_with(strict=True)


@pytest.mark.asyncio
async def test_update_theme_matches_by_id_and_returns_updated_entity() -> None:
    theme = make_theme()
    theme.update(
        label="Consciência de si",
        description="Descrição atualizada.",
        updated_at=datetime(2026, 9, 18, 13, 0, tzinfo=timezone.utc),
    )
    result = make_result({"theme": node_from(theme)})
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = ThemeRepository(transaction, ThemeMapper())

    updated = await repository.update_theme(theme)

    assert_same_theme(updated, theme)
    assert transaction.run.await_args.kwargs == {
        "theme_id": theme.id.value,
        "properties": node_from(theme),
    }


@pytest.mark.asyncio
async def test_delete_theme_consumes_the_write_result() -> None:
    theme_id = ThemeId("01THEME0000000000000000000")
    result = make_result()
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = ThemeRepository(transaction, ThemeMapper())

    await repository.delete_theme(theme_id)

    assert transaction.run.await_args.kwargs["theme_id"] == theme_id.value
    result.consume.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_list_themes_maps_every_returned_node() -> None:
    first = make_theme("01THEME0000000000000000000")
    second = make_theme("01THEME0000000000000000001")
    result = make_result(
        {"theme": node_from(first)},
        {"theme": node_from(second)},
    )
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = ThemeRepository(transaction, ThemeMapper())

    themes = await repository.list_themes()

    assert len(themes) == 2
    assert_same_theme(themes[0], first)
    assert_same_theme(themes[1], second)


@pytest.mark.asyncio
async def test_create_many_themes_uses_one_query_and_preserves_result_order() -> None:
    first = make_theme("01THEME0000000000000000000")
    second = make_theme("01THEME0000000000000000001")
    result = make_result(
        {"theme": node_from(first)},
        {"theme": node_from(second)},
    )
    transaction = AsyncMock()
    transaction.run.return_value = result
    repository = ThemeRepository(transaction, ThemeMapper())

    created = await repository.create_many_themes([first, second])

    assert len(created) == 2
    assert_same_theme(created[0], first)
    assert_same_theme(created[1], second)
    assert transaction.run.await_count == 1
    assert transaction.run.await_args.kwargs["themes"] == [
        node_from(first),
        node_from(second),
    ]


@pytest.mark.asyncio
async def test_create_many_themes_skips_database_for_empty_collection() -> None:
    transaction = AsyncMock()
    repository = ThemeRepository(transaction, ThemeMapper())

    created = await repository.create_many_themes([])

    assert created == []
    transaction.run.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_many_themes_translates_neo4j_constraint_error() -> None:
    transaction = AsyncMock()
    transaction.run.side_effect = ConstraintError("duplicate slug")
    repository = ThemeRepository(transaction, ThemeMapper())

    with pytest.raises(ThemeAlreadyExistsError) as raised:
        await repository.create_many_themes([make_theme()])

    assert raised.value.status_code == 409
    assert isinstance(raised.value.__cause__, ConstraintError)
