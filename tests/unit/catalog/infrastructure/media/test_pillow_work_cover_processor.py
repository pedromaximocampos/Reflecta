from io import BytesIO

import pytest
from PIL import Image

from src.modules.catalog.domain.exceptions.work_exceptions import (
    InvalidWorkCoverError,
)
from src.modules.catalog.infrastructure.media import PillowWorkCoverProcessor


def make_image(image_format: str = "PNG") -> BytesIO:
    content = BytesIO()
    Image.new("RGB", (2000, 3000), color=(42, 66, 48)).save(
        content,
        format=image_format,
    )
    content.seek(0)
    return content


@pytest.mark.asyncio
async def test_processor_validates_resizes_and_normalizes_to_webp() -> None:
    content = make_image()

    processed = await PillowWorkCoverProcessor().process(
        content=content,
        declared_content_type="image/png",
        declared_size_bytes=content.getbuffer().nbytes,
    )

    assert processed.content_type == "image/webp"
    assert processed.extension == "webp"
    with Image.open(processed.content) as normalized:
        assert normalized.format == "WEBP"
        assert normalized.width <= 1600
        assert normalized.height <= 2400


@pytest.mark.asyncio
async def test_processor_rejects_mismatched_or_corrupted_content() -> None:
    png = make_image()
    with pytest.raises(InvalidWorkCoverError):
        await PillowWorkCoverProcessor().process(
            content=png,
            declared_content_type="image/jpeg",
            declared_size_bytes=png.getbuffer().nbytes,
        )

    corrupted = BytesIO(b"not-an-image")
    with pytest.raises(InvalidWorkCoverError):
        await PillowWorkCoverProcessor().process(
            content=corrupted,
            declared_content_type="image/png",
            declared_size_bytes=corrupted.getbuffer().nbytes,
        )
