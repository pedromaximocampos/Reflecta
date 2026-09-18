from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThemeId:
    value: str