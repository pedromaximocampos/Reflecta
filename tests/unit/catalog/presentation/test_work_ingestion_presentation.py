from io import BytesIO
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from src.modules.catalog.application.use_cases.request_work_ingestion import (
    RequestWorkIngestionOutputDTO,
)
from src.modules.catalog.domain.value_objects.work_ingestion_status import (
    WorkIngestionStatus,
)
from src.modules.catalog.presentation.controllers.request_work_ingestion_controller import (
    RequestWorkIngestionController,
)
from src.modules.catalog.presentation.validators.request_work_ingestion import (
    WorkDocumentUploadValidator,
)
from src.modules.catalog.public.work_id import WorkId
from src.modules.catalog.public.work_ingestion_id import WorkIngestionId
from src.shared.presentation.http_types import HttpRequest


WORK_ID = "01WORK00000000000000000000"
INGESTION_ID = "01INGESTION000000000000000"
ADMIN_ID = "01ADMIN0000000000000000000"


def test_work_document_validator_accepts_pdf_metadata() -> None:
    validated = WorkDocumentUploadValidator.model_validate(
        {
            "filename": "meditacoes.pdf",
            "content_type": "application/pdf",
            "size_bytes": 1024,
        }
    )

    assert validated.filename == "meditacoes.pdf"


@pytest.mark.parametrize(
    ("filename", "content_type", "size_bytes"),
    [
        ("meditacoes.txt", "application/pdf", 1024),
        ("meditacoes.pdf", "text/plain", 1024),
        ("meditacoes.pdf", "application/pdf", 0),
        ("folder/meditacoes.pdf", "application/pdf", 1024),
    ],
)
def test_work_document_validator_rejects_invalid_http_metadata(
    filename: str,
    content_type: str,
    size_bytes: int,
) -> None:
    with pytest.raises(ValidationError):
        WorkDocumentUploadValidator.model_validate(
            {
                "filename": filename,
                "content_type": content_type,
                "size_bytes": size_bytes,
            }
        )


@pytest.mark.asyncio
async def test_request_work_ingestion_controller_builds_application_input() -> None:
    use_case = AsyncMock()
    use_case.execute.return_value = RequestWorkIngestionOutputDTO(
        ingestion_id=WorkIngestionId(INGESTION_ID),
        work_id=WorkId(WORK_ID),
        status=WorkIngestionStatus.PENDING,
    )
    controller = RequestWorkIngestionController(use_case)
    content = BytesIO(b"%PDF-1.7")

    response = await controller.handle_request(
        HttpRequest(
            method="POST",
            url=f"http://test/catalog/works/{WORK_ID}/ingestions",
            body={
                "filename": "meditacoes.pdf",
                "content_type": "application/pdf",
                "size_bytes": 8,
                "content": content,
            },
            path_params={"work_id": WORK_ID},
            authenticated_user_id=ADMIN_ID,
        )
    )

    ingestion_input = use_case.execute.await_args.args[0]
    assert ingestion_input.work_id.value == WORK_ID
    assert ingestion_input.requested_by.value == ADMIN_ID
    assert ingestion_input.content is content
    assert response.status_code == 202
    assert response.body == {
        "ingestion_id": INGESTION_ID,
        "work_id": WORK_ID,
        "status": "pending",
    }
