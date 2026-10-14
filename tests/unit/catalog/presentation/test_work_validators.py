import pytest
from pydantic import ValidationError

from src.modules.catalog.presentation.validators.create_work import CreateWorkValidator


def test_create_work_validator_accepts_catalog_metadata() -> None:
    payload = CreateWorkValidator.model_validate(
        {
            "title": "Meditações",
            "synopsis": "Reflexões estoicas.",
            "type": "BOOK",
            "language": "pt-BR",
            "author": {"name": "Marco Aurélio", "description": "Filósofo estoico."},
        }
    )
    assert payload.author.name == "Marco Aurélio"
    assert payload.type == "BOOK"


def test_create_work_validator_rejects_client_controlled_file_url() -> None:
    with pytest.raises(ValidationError):
        CreateWorkValidator.model_validate(
            {
                "title": "Meditações",
                "synopsis": "Reflexões estoicas.",
                "type": "BOOK",
                "language": "pt-BR",
                "author": {"name": "Marco Aurélio"},
                "source_file_url": "https://example.test/file.pdf",
            }
        )
