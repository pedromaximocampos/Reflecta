import asyncio
import re
from collections import Counter

from src.modules.catalog.infrastructure.system import VibrantThemeColorGenerator
from src.shared.infrastructure.persistence.neo4j.connection import Neo4jConnectionHandler
from src.shared.infrastructure.persistence.neo4j.provider import reflecta_neo4j_provider

_HEX_COLOR = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _normalized_color(value: object) -> str | None:
    if not isinstance(value, str) or _HEX_COLOR.fullmatch(value) is None:
        return None
    return value.upper()


async def backfill_theme_colors(connection: Neo4jConnectionHandler) -> int:
    """Repair missing/duplicated colors and enforce uniqueness in Neo4j."""
    generator = VibrantThemeColorGenerator()

    async with connection.session() as session:
        result = await session.run(
            """
            MATCH (theme:Theme)
            RETURN theme.theme_id AS theme_id, theme.color AS color
            ORDER BY theme.theme_id
            """
        )
        themes = [record async for record in result]

        normalized_colors = [_normalized_color(record["color"]) for record in themes]
        color_counts = Counter(color for color in normalized_colors if color is not None)
        reserved = {color for color, count in color_counts.items() if count == 1}
        updates: list[dict[str, str]] = []

        for record, current_color in zip(themes, normalized_colors, strict=True):
            if current_color is not None and color_counts[current_color] == 1:
                continue

            color = generator.generate(reserved)
            reserved.add(color)
            updates.append({"theme_id": record["theme_id"], "color": color})

        if updates:
            update_result = await session.run(
                """
                UNWIND $updates AS update
                MATCH (theme:Theme {theme_id: update.theme_id})
                SET theme.color = update.color
                """,
                updates=updates,
            )
            await update_result.consume()

        constraint_result = await session.run(
            """
            CREATE CONSTRAINT theme_color_unique IF NOT EXISTS
            FOR (theme:Theme)
            REQUIRE theme.color IS UNIQUE
            """
        )
        await constraint_result.consume()

    return len(updates)


async def _main() -> None:
    try:
        await reflecta_neo4j_provider.verify_connection()
        updated = await backfill_theme_colors(reflecta_neo4j_provider)
        print(f"Theme color migration completed: {updated} theme(s) updated.")
    finally:
        await reflecta_neo4j_provider.close()


if __name__ == "__main__":
    asyncio.run(_main())
