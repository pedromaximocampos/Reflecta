from dataclasses import dataclass
from typing import BinaryIO, Literal

from fastapi import File, UploadFile
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from src.modules.auth.domain.value_objects.user_avatar_constraints import (
    USER_AVATAR_MAX_SIZE_BYTES,
)


class UserAvatarUploadValidator(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str = Field(..., min_length=1, max_length=255)
    content_type: Literal["image/jpeg", "image/png", "image/webp"]
    size_bytes: int = Field(..., gt=0, le=USER_AVATAR_MAX_SIZE_BYTES)

    @field_validator("filename")
    @classmethod
    def validate_image_filename(cls, filename: str) -> str:
        normalized = filename.strip()
        if "/" in normalized or "\\" in normalized:
            raise ValueError("filename must not contain a path")
        if not normalized.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            raise ValueError("avatar filename must be JPEG, PNG, or WebP")
        return normalized


@dataclass(frozen=True, slots=True)
class ValidatedUserAvatarUpload:
    filename: str
    content_type: str
    size_bytes: int
    content: BinaryIO


async def validate_user_avatar_upload(
    avatar: UploadFile = File(
        ...,
        description=(
            "JPEG, PNG, or WebP profile photo up to 5 MB and at least "
            "128 by 128 pixels"
        ),
    ),
) -> ValidatedUserAvatarUpload:
    try:
        metadata = UserAvatarUploadValidator.model_validate(
            {
                "filename": avatar.filename or "",
                "content_type": avatar.content_type or "",
                "size_bytes": avatar.size or 0,
            }
        )
    except ValidationError as error:
        raise RequestValidationError(error.errors()) from error

    return ValidatedUserAvatarUpload(
        filename=metadata.filename,
        content_type=metadata.content_type,
        size_bytes=metadata.size_bytes,
        content=avatar.file,
    )
