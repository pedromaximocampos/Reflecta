from collections.abc import Mapping
from typing import Any

from neo4j import AsyncTransaction
from neo4j.exceptions import ConstraintError

from src.modules.catalog.domain.entities.theme import Theme
from src.modules.catalog.domain.exceptions.theme_exceptions import ThemeAlreadyExistsError
from src.modules.catalog.domain.ports.repositories.itheme_repository import (
    IThemeRepository,
)
from src.modules.catalog.public.theme_id import ThemeId
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class ThemeRepository(IThemeRepository):
    def __init__(
        self,
        transaction: AsyncTransaction,
        theme_mapper: IMapper[Mapping[str, Any], Theme],
    ) -> None:
        self._transaction = transaction
        self._mapper = theme_mapper

    async def get_theme_by_id(self, theme_id: ThemeId) -> Theme | None:
        result = await self._transaction.run(
            """
            MATCH (theme:Theme {theme_id: $theme_id})
            RETURN theme
            """,
            theme_id=theme_id.value,
        )
        record = await result.single()

        if record is None:
            return None

        return self._mapper.to_entity(record["theme"])

    async def create_theme(self, theme: Theme) -> Theme:
        try:
            result = await self._transaction.run(
                """
                CREATE (created_theme:Theme)
                SET created_theme = $properties
                RETURN created_theme AS theme
                """,
                properties=dict(self._mapper.to_model(theme)),
            )
            record = await result.single(strict=True)
            return self._mapper.to_entity(record["theme"])
        except ConstraintError as error:
            raise ThemeAlreadyExistsError(theme.slug) from error

    async def update_theme(self, theme: Theme) -> Theme:
        result = await self._transaction.run(
            """
            MATCH (stored_theme:Theme {theme_id: $theme_id})
            SET stored_theme = $properties
            RETURN stored_theme AS theme
            """,
            theme_id=theme.id.value,
            properties=dict(self._mapper.to_model(theme)),
        )
        record = await result.single(strict=True)
        return self._mapper.to_entity(record["theme"])

    async def delete_theme(self, theme_id: ThemeId) -> None:
        result = await self._transaction.run(
            """
            MATCH (theme:Theme {theme_id: $theme_id})
            DETACH DELETE theme
            """,
            theme_id=theme_id.value,
        )
        await result.consume()

    async def list_themes(self) -> list[Theme]:
        result = await self._transaction.run(
            """
            MATCH (theme:Theme)
            RETURN theme
            ORDER BY theme.label, theme.theme_id
            """
        )

        return [
            self._mapper.to_entity(record["theme"])
            async for record in result
        ]

    async def create_many_themes(self, themes: list[Theme]) -> list[Theme]:
        if not themes:
            return []

        properties = [dict(self._mapper.to_model(theme)) for theme in themes]
        try:
            result = await self._transaction.run(
                """
                UNWIND range(0, size($themes) - 1) AS position
                WITH position, $themes[position] AS properties
                CREATE (created_theme:Theme)
                SET created_theme = properties
                RETURN created_theme AS theme
                ORDER BY position
                """,
                themes=properties,
            )

            return [
                self._mapper.to_entity(record["theme"])
                async for record in result
            ]
        except ConstraintError as error:
            raise ThemeAlreadyExistsError() from error

    async def get_theme_by_slug(self, slug: str) -> Theme | None:
        result = await self._transaction.run(
            """
            MATCH (theme:Theme {slug: $slug})
            RETURN theme
            """,
            slug=slug,
        )
        record = await result.single()

        if record is None:
            return None

        return self._mapper.to_entity(record["theme"])
