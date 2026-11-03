from dataclasses import dataclass
from typing import BinaryIO, Literal

from fastapi import File, UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from src.modules.catalog.domain.value_objects.work_cover_constraints import (
    WORK_COVER_MAX_SIZE_BYTES,
)


class WorkCoverUploadValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str = Field(..., min_length=1, max_length=255)
    content_type: Literal["image/jpeg", "image/png", "image/webp"]
    size_bytes: int = Field(..., gt=0, le=WORK_COVER_MAX_SIZE_BYTES)

    @field_validator("filename")
    @classmethod
    def validate_image_filename(cls, filename: str) -> str:
        normalized = filename.strip()
        if "/" in normalized or "\\" in normalized:
            raise ValueError("filename must not contain a path")
        if not normalized.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            raise ValueError("cover filename must be JPEG, PNG, or WebP")
        return normalized


@dataclass(frozen=True, slots=True)
class ValidatedWorkCoverUpload:
    filename: str
    content_type: str
    size_bytes: int
    content: BinaryIO


async def validate_work_cover_upload(
    cover: UploadFile = File(
        ...,
        description="JPEG, PNG, or WebP cover image up to 5 MB",
    ),
) -> ValidatedWorkCoverUpload:
    try:
        metadata = WorkCoverUploadValidator.model_validate(
            {
                "filename": cover.filename or "",
                "content_type": cover.content_type or "",
                "size_bytes": cover.size or 0,
            }
        )
    except ValidationError as error:
        raise RequestValidationError(error.errors()) from error

    return ValidatedWorkCoverUpload(
        filename=metadata.filename,
        content_type=metadata.content_type,
        size_bytes=metadata.size_bytes,
        content=cover.file,
    )
