from io import BytesIO

import pytest
from PIL import Image

from src.modules.auth.domain.exceptions.user_custom_exceptions import (
    InvalidUserAvatarError,
)
from src.modules.auth.infrastructure.media import PillowUserAvatarProcessor


def make_image(size=(800, 1200), image_format: str = "PNG") -> BytesIO:
    content = BytesIO()
    Image.new("RGB", size, color=(42, 66, 48)).save(content, format=image_format)
    content.seek(0)
    return content


@pytest.mark.asyncio
async def test_processor_crops_and_normalizes_avatar_to_square_webp() -> None:
    content = make_image()

    processed = await PillowUserAvatarProcessor().process(
        content=content,
        declared_content_type="image/png",
        declared_size_bytes=content.getbuffer().nbytes,
    )

    assert processed.content_type == "image/webp"
    assert processed.extension == "webp"
    with Image.open(processed.content) as normalized:
        assert normalized.format == "WEBP"
        assert normalized.size == (512, 512)


@pytest.mark.asyncio
async def test_processor_rejects_small_mismatched_or_corrupted_avatar() -> None:
    small = make_image(size=(64, 64))
    with pytest.raises(InvalidUserAvatarError):
        await PillowUserAvatarProcessor().process(
            content=small,
            declared_content_type="image/png",
            declared_size_bytes=small.getbuffer().nbytes,
        )

    png = make_image()
    with pytest.raises(InvalidUserAvatarError):
        await PillowUserAvatarProcessor().process(
            content=png,
            declared_content_type="image/jpeg",
            declared_size_bytes=png.getbuffer().nbytes,
        )

    corrupted = BytesIO(b"not-an-image")
    with pytest.raises(InvalidUserAvatarError):
        await PillowUserAvatarProcessor().process(
            content=corrupted,
            declared_content_type="image/png",
            declared_size_bytes=corrupted.getbuffer().nbytes,
        )
