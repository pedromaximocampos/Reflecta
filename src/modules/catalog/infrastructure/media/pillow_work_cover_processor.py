import asyncio
import warnings
from io import BytesIO
from typing import BinaryIO

from PIL import Image, ImageOps, UnidentifiedImageError

from src.modules.catalog.application.dto import ProcessedWorkCoverDTO
from src.modules.catalog.application.ports.media import IWorkCoverProcessor
from src.modules.catalog.domain.exceptions.work_exceptions import (
    InvalidWorkCoverError,
)
from src.modules.catalog.domain.value_objects.work_cover_constraints import (
    WORK_COVER_ALLOWED_CONTENT_TYPES,
    WORK_COVER_MAX_SIZE_BYTES,
)


class PillowWorkCoverProcessor(IWorkCoverProcessor):
    _MAX_DIMENSIONS = (1600, 2400)
    _MAX_IMAGE_PIXELS = 20_000_000
    _FORMAT_CONTENT_TYPES = {
        "JPEG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp",
    }

    async def process(
        self,
        *,
        content: BinaryIO,
        declared_content_type: str,
        declared_size_bytes: int,
    ) -> ProcessedWorkCoverDTO:
        return await asyncio.to_thread(
            self._process_sync,
            content,
            declared_content_type,
            declared_size_bytes,
        )

    def _process_sync(
        self,
        content: BinaryIO,
        declared_content_type: str,
        declared_size_bytes: int,
    ) -> ProcessedWorkCoverDTO:
        normalized_type = declared_content_type.lower()
        if normalized_type not in WORK_COVER_ALLOWED_CONTENT_TYPES:
            raise InvalidWorkCoverError("The work cover must be JPEG, PNG, or WebP.")
        if not 0 < declared_size_bytes <= WORK_COVER_MAX_SIZE_BYTES:
            raise InvalidWorkCoverError("The work cover must not exceed 5 MB.")
        if not content.seekable():
            raise InvalidWorkCoverError("The work cover stream must be seekable.")

        try:
            content.seek(0)
            raw_content = content.read(WORK_COVER_MAX_SIZE_BYTES + 1)
            content.seek(0)
        except (OSError, ValueError) as error:
            raise InvalidWorkCoverError(
                "The work cover could not be inspected."
            ) from error

        if len(raw_content) != declared_size_bytes:
            raise InvalidWorkCoverError("The work cover size is inconsistent.")

        original_max_pixels = Image.MAX_IMAGE_PIXELS
        try:
            Image.MAX_IMAGE_PIXELS = self._MAX_IMAGE_PIXELS
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(raw_content)) as source:
                    source.seek(0)
                    actual_type = self._FORMAT_CONTENT_TYPES.get(source.format or "")
                    if actual_type is None or actual_type != normalized_type:
                        raise InvalidWorkCoverError(
                            "The work cover content does not match its declared type."
                        )
                    source.load()
                    normalized = ImageOps.exif_transpose(source)
                    normalized.thumbnail(self._MAX_DIMENSIONS, Image.Resampling.LANCZOS)
                    target_mode = "RGBA" if "A" in normalized.getbands() else "RGB"
                    converted = normalized.convert(target_mode)
                    output = BytesIO()
                    converted.save(
                        output,
                        format="WEBP",
                        quality=85,
                        method=6,
                    )
                    output.seek(0)
        except InvalidWorkCoverError:
            raise
        except (
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
            UnidentifiedImageError,
            OSError,
            ValueError,
        ) as error:
            raise InvalidWorkCoverError(
                "The work cover is corrupted or unsafe to process."
            ) from error
        finally:
            Image.MAX_IMAGE_PIXELS = original_max_pixels

        return ProcessedWorkCoverDTO(
            content=output,
            content_type="image/webp",
            size_bytes=output.getbuffer().nbytes,
            extension="webp",
        )
