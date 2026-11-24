from typing import Protocol, TypedDict


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

