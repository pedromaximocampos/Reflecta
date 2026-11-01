import pytest
from pydantic import ValidationError

from src.modules.catalog.presentation.validators.update_theme import UpdateThemeValidator


def test_update_theme_validator_accepts_partial_update() -> None:
    validator = UpdateThemeValidator(is_active=False)

    assert validator.model_dump(exclude_unset=True) == {"is_active": False}


@pytest.mark.parametrize("field", ["label", "description", "is_active"])
def test_update_theme_validator_rejects_explicit_null(field: str) -> None:
    with pytest.raises(ValidationError):
        UpdateThemeValidator.model_validate({field: None})


@pytest.mark.parametrize("color", ["#12abef", "", None, "not-a-color", 123456])
def test_create_theme_accepts_and_discards_legacy_color(color) -> None:
    from src.modules.catalog.presentation.validators.create_theme import ThemeValidator

    validator = ThemeValidator(
        label="Trabalho",
        description="Vida profissional",
        color=color,
    )

    assert validator.model_dump() == {
        "label": "Trabalho",
        "description": "Vida profissional",
        "is_active": True,
    }


@pytest.mark.parametrize("color", ["#12abef", "", None, "not-a-color", 123456])
def test_update_theme_accepts_and_discards_legacy_color(color) -> None:
    validator = UpdateThemeValidator(label="Novo nome", color=color)

    assert validator.model_dump(exclude_unset=True) == {"label": "Novo nome"}


def test_created_theme_response_still_requires_a_valid_color() -> None:
    from datetime import datetime, timezone
    from src.modules.catalog.presentation.validators.create_theme import CreatedThemeValidator

    created = CreatedThemeValidator(
        id="theme-id",
        slug="trabalho",
        label="Trabalho",
        description="Vida profissional",
        is_active=True,
        color="#12abef",
        created_at=datetime(2026, 11, 1, tzinfo=timezone.utc),
    )

    assert created.color == "#12ABEF"
