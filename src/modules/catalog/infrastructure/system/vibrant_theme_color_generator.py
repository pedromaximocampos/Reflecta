import colorsys
import secrets
from collections.abc import Callable, Collection

from src.modules.catalog.public.theme_color import normalize_theme_color


class VibrantThemeColorGenerator:
    """Generates saturated colors while excluding every already reserved value."""

    _MAX_RANDOM_ATTEMPTS = 4_096

    def __init__(self, randbelow: Callable[[int], int] = secrets.randbelow) -> None:
        self._randbelow = randbelow

    def generate(self, used_colors: Collection[str]) -> str:
        reserved = self._normalize_reserved_colors(used_colors)

        for _ in range(self._MAX_RANDOM_ATTEMPTS):
            hue = self._randbelow(360)
            saturation = 72 + self._randbelow(19)
            lightness = 45 + self._randbelow(14)
            color = self._hsl_to_hex(hue, saturation, lightness)
            if color not in reserved:
                return color

        # Deterministic fallback keeps creation possible even with an unlucky RNG.
        for lightness in range(45, 59):
            for saturation in range(72, 91):
                for hue in range(360):
                    color = self._hsl_to_hex(hue, saturation, lightness)
                    if color not in reserved:
                        return color

        raise RuntimeError("The vibrant theme color space has been exhausted.")

    @staticmethod
    def _normalize_reserved_colors(used_colors: Collection[str]) -> set[str]:
        normalized: set[str] = set()
        for color in used_colors:
            try:
                normalized.add(normalize_theme_color(color))
            except ValueError:
                continue
        return normalized

    @staticmethod
    def _hsl_to_hex(hue: int, saturation: int, lightness: int) -> str:
        red, green, blue = colorsys.hls_to_rgb(
            hue / 360,
            lightness / 100,
            saturation / 100,
        )
        return f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"
