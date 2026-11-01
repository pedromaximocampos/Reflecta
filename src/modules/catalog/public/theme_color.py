import re
from typing import Annotated

from pydantic import StringConstraints

DEFAULT_THEME_COLOR = "#8B5CF6"
ThemeColor = Annotated[str, StringConstraints(strict=True, pattern=r"^#[0-9a-fA-F]{6}$", to_upper=True)]


def normalize_theme_color(color: str) -> str:
    if not isinstance(color, str) or re.fullmatch(r"#[0-9a-fA-F]{6}", color) is None:
        raise ValueError("Theme color must use #RRGGBB format.")
    return color.upper()
