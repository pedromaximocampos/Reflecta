from dataclasses import dataclass
from typing import BinaryIO, Literal

from fastapi import File, UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class WorkDocumentUploadValidator(BaseModel):
    """Validates only the HTTP metadata of an uploaded work document."""

    model_config = ConfigDict(extra="forbid")

    filename: str = Field(..., min_length=1, max_length=255)
    content_type: Literal["application/pdf"]
    size_bytes: int = Field(..., gt=0)

    @field_validator("filename")
    @classmethod
    def validate_pdf_filename(cls, filename: str) -> str:
        normalized = filename.strip()
        if "/" in normalized or "\\" in normalized:
            raise ValueError("filename must not contain a path")
        if not normalized.lower().endswith(".pdf"):
            raise ValueError("document filename must use the .pdf extension")
        return normalized


@dataclass(frozen=True, slots=True)
class ValidatedWorkDocumentUpload:
    filename: str
    content_type: str
    size_bytes: int
    content: BinaryIO


async def validate_work_document_upload(
    document: UploadFile = File(
        ...,
        description="PDF source document that will be processed by the catalog ingestion",
    ),
) -> ValidatedWorkDocumentUpload:
    try:
        metadata = WorkDocumentUploadValidator.model_validate(
            {
                "filename": document.filename or "",
                "content_type": document.content_type or "",
                "size_bytes": document.size or 0,
            }
        )
    except ValidationError as error:
        raise RequestValidationError(error.errors()) from error

    return ValidatedWorkDocumentUpload(
        filename=metadata.filename,
        content_type=metadata.content_type,
        size_bytes=metadata.size_bytes,
        content=document.file,
    )


class WorkIngestionAcceptedValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ingestion_id: str = Field(..., min_length=26, max_length=26)
    work_id: str = Field(..., min_length=26, max_length=26)
    status: Literal["pending"]
