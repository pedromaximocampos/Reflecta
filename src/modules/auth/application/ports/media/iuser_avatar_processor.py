from typing import BinaryIO, Protocol

from src.modules.auth.application.dto import ProcessedUserAvatarDTO


class IUserAvatarProcessor(Protocol):
    async def process(
        self,
        *,
        content: BinaryIO,
        declared_content_type: str,
        declared_size_bytes: int,
    ) -> ProcessedUserAvatarDTO: ...
