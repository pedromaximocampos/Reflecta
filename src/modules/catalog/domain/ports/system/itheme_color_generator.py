from collections.abc import Collection
from typing import Protocol


class IThemeColorGenerator(Protocol):
    def generate(self, used_colors: Collection[str]) -> str:
        """Generate a vibrant #RRGGBB color not present in used_colors."""
        ...
