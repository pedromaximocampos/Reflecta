import asyncio
import warnings
from io import BytesIO
from typing import BinaryIO

from PIL import Image, ImageOps, UnidentifiedImageError

from src.modules.auth.application.dto import ProcessedUserAvatarDTO
from src.modules.auth.application.ports.media import IUserAvatarProcessor
from src.modules.auth.domain.exceptions.user_custom_exceptions import (
    InvalidUserAvatarError,
)
from src.modules.auth.domain.value_objects.user_avatar_constraints import (
    USER_AVATAR_ALLOWED_CONTENT_TYPES,
    USER_AVATAR_MAX_SIZE_BYTES,
    USER_AVATAR_MIN_DIMENSION_PIXELS,
    USER_AVATAR_OUTPUT_DIMENSION_PIXELS,
)


class PillowUserAvatarProcessor(IUserAvatarProcessor):
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
    ) -> ProcessedUserAvatarDTO:
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
    ) -> ProcessedUserAvatarDTO:
        normalized_type = declared_content_type.lower()
        if normalized_type not in USER_AVATAR_ALLOWED_CONTENT_TYPES:
            raise InvalidUserAvatarError("A foto deve ser JPEG, PNG ou WebP.")
        if not 0 < declared_size_bytes <= USER_AVATAR_MAX_SIZE_BYTES:
            raise InvalidUserAvatarError("A foto não pode ultrapassar 5 MB.")
        if not content.seekable():
            raise InvalidUserAvatarError("Não foi possível inspecionar a foto.")

        try:
            content.seek(0)
            raw_content = content.read(USER_AVATAR_MAX_SIZE_BYTES + 1)
            content.seek(0)
        except (OSError, ValueError) as error:
            raise InvalidUserAvatarError(
                "Não foi possível inspecionar a foto."
            ) from error

        if len(raw_content) != declared_size_bytes:
            raise InvalidUserAvatarError("O tamanho informado da foto é inconsistente.")

        original_max_pixels = Image.MAX_IMAGE_PIXELS
        try:
            Image.MAX_IMAGE_PIXELS = self._MAX_IMAGE_PIXELS
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(raw_content)) as source:
                    source.seek(0)
                    actual_type = self._FORMAT_CONTENT_TYPES.get(source.format or "")
                    if actual_type is None or actual_type != normalized_type:
                        raise InvalidUserAvatarError(
                            "O conteúdo da foto não corresponde ao formato informado."
                        )
                    source.load()
                    normalized = ImageOps.exif_transpose(source)
                    if min(normalized.size) < USER_AVATAR_MIN_DIMENSION_PIXELS:
                        raise InvalidUserAvatarError(
                            "A foto deve ter pelo menos 128 por 128 pixels."
                        )
                    fitted = ImageOps.fit(
                        normalized,
                        (
                            USER_AVATAR_OUTPUT_DIMENSION_PIXELS,
                            USER_AVATAR_OUTPUT_DIMENSION_PIXELS,
                        ),
                        method=Image.Resampling.LANCZOS,
                        centering=(0.5, 0.5),
                    )
                    target_mode = "RGBA" if "A" in fitted.getbands() else "RGB"
                    converted = fitted.convert(target_mode)
                    output = BytesIO()
                    converted.save(output, format="WEBP", quality=85, method=6)
                    output.seek(0)
        except InvalidUserAvatarError:
            raise
        except (
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
            UnidentifiedImageError,
            OSError,
            ValueError,
        ) as error:
            raise InvalidUserAvatarError(
                "A foto está corrompida ou não é segura para processamento."
            ) from error
        finally:
            Image.MAX_IMAGE_PIXELS = original_max_pixels

        return ProcessedUserAvatarDTO(
            content=output,
            content_type="image/webp",
            size_bytes=output.getbuffer().nbytes,
            extension="webp",
        )
