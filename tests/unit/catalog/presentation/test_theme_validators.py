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
