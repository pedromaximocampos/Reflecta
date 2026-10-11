import pytest
from pydantic import ValidationError

from src.modules.catalog.presentation.validators.passage import (
    CreatePassageValidator,
    UpdatePassageValidator,
)


THEME_ID = "01ARZ3NDEKTSV4RRFFQ69G5FAW"
WORK_ID = "01ARZ3NDEKTSV4RRFFQ69G5FAV"


def _valid_create_body() -> dict:
    return {
        "work_id": WORK_ID,
        "locator": "cap. 1",
        "short_text": "Uma passagem suficientemente longa para o catálogo.",
        "paraphrase": "Paráfrase revisável.",
        "interpretation_note": "Nota interpretativa.",
        "themes": [{"theme_id": THEME_ID, "confidence": 1.0}],
    }


def test_create_rejects_duplicate_theme_ids() -> None:
    body = _valid_create_body()
    body["themes"] = [body["themes"][0], body["themes"][0]]

    with pytest.raises(ValidationError, match="theme_id values must be unique"):
        CreatePassageValidator.model_validate(body)


def test_update_accepts_explicit_nulls_to_clear_page_range() -> None:
    validated = UpdatePassageValidator.model_validate(
        {"start_page": None, "end_page": None}
    )

    assert validated.model_dump(exclude_unset=True) == {
        "start_page": None,
        "end_page": None,
    }


def test_update_requires_both_page_fields_even_when_null() -> None:
    with pytest.raises(
        ValidationError,
        match="start_page and end_page must be provided together",
    ):
        UpdatePassageValidator.model_validate({"start_page": None})
