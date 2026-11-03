from typing import BinaryIO, Protocol

from src.modules.auth.application.dto import StoredUserAvatarDTO


class IUserAvatarStorage(Protocol):
    async def upload(
        self,
        *,
        object_key: str,
        content: BinaryIO,
        content_type: str,
        size_bytes: int,
    ) -> StoredUserAvatarDTO: ...

    async def delete(self, *, object_key: str) -> None: ...

    async def create_read_url(self, *, object_key: str) -> str: ...
