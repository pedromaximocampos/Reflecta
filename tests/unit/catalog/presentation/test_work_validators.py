import pytest
from pydantic import ValidationError

from src.modules.catalog.presentation.validators.create_work import CreateWorkValidator
from src.modules.catalog.presentation.validators.work_cover import (
    WorkCoverUploadValidator,
)


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


def test_create_work_validator_rejects_client_controlled_cover_url() -> None:
    with pytest.raises(ValidationError):
        CreateWorkValidator.model_validate(
            {
                "title": "Meditações",
                "synopsis": "Reflexões estoicas.",
                "type": "BOOK",
                "language": "pt-BR",
                "author": {"name": "Marco Aurélio"},
                "cover_image_url": "not-a-url",
            }
        )


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


def test_work_cover_validator_accepts_supported_metadata() -> None:
    upload = WorkCoverUploadValidator.model_validate(
        {
            "filename": "cover.webp",
            "content_type": "image/webp",
            "size_bytes": 1024,
        }
    )
    assert upload.filename == "cover.webp"


def test_work_cover_validator_rejects_unsupported_or_oversized_file() -> None:
    with pytest.raises(ValidationError):
        WorkCoverUploadValidator.model_validate(
            {
                "filename": "cover.gif",
                "content_type": "image/gif",
                "size_bytes": 1024,
            }
        )
    with pytest.raises(ValidationError):
        WorkCoverUploadValidator.model_validate(
            {
                "filename": "cover.png",
                "content_type": "image/png",
                "size_bytes": 6 * 1024 * 1024,
            }
        )
