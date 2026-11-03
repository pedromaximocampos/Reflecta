import re

from src.modules.catalog.infrastructure.system import VibrantThemeColorGenerator


class SequentialRandBelow:
    def __init__(self, *values: int) -> None:
        self._values = iter(values)

    def __call__(self, upper_bound: int) -> int:
        return next(self._values) % upper_bound


def test_generator_returns_normalized_vibrant_hex_color() -> None:
    generator = VibrantThemeColorGenerator(SequentialRandBelow(210, 10, 7))

    color = generator.generate(set())

    assert re.fullmatch(r"#[0-9A-F]{6}", color)
    assert color == "#2085E9"


def test_generator_skips_a_color_already_in_use() -> None:
    random_values = SequentialRandBelow(
        210, 10, 7,
        25, 4, 3,
    )
    generator = VibrantThemeColorGenerator(random_values)
    first_color = VibrantThemeColorGenerator(
        SequentialRandBelow(210, 10, 7)
    ).generate(set())

    second_color = generator.generate({first_color.lower()})

    assert second_color != first_color
    assert re.fullmatch(r"#[0-9A-F]{6}", second_color)
