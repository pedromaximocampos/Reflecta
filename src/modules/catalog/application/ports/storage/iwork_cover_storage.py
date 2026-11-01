from typing import BinaryIO, Protocol

from src.modules.catalog.application.dto import StoredWorkCoverDTO


class IWorkCoverStorage(Protocol):
    async def upload(
        self,
        *,
        object_key: str,
        content: BinaryIO,
        content_type: str,
        size_bytes: int,
    ) -> StoredWorkCoverDTO: ...

    async def delete(self, *, object_key: str) -> None: ...

    async def create_read_url(self, *, object_key: str) -> str: ...
