from typing import Any, Protocol, TypedDict


class ThemeAffinity(TypedDict):
    theme_id: str
    slug: str
    label: str
    color: str | None
    reflection_count: int


class IJournalInsightsReader(Protocol):
    async def theme_affinities(
        self,
        user_id: str,
        *,
        limit: int = 5,
    ) -> tuple[ThemeAffinity, ...]: ...


class IJournalHomeReader(IJournalInsightsReader, Protocol):
    async def home_snapshot(
        self,
        user_id: str,
        *,
        entry_limit: int = 5,
        entry_offset: int = 0,
    ) -> dict[str, Any]: ...

