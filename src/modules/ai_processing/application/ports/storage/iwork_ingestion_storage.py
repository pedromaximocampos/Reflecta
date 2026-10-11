from typing import BinaryIO, Protocol

from src.modules.ai_processing.application.dto import (
    StorageObjectLocationDTO,
    StoredNormalizedTextDTO,
)


class IWorkIngestionStorage(Protocol):
    async def download_document(
        self,
        *,
        location: StorageObjectLocationDTO,
        destination: BinaryIO,
    ) -> None: ...

    async def save_normalized_text(
        self,
        *,
        object_key: str,
        text: str,
        normalizer_version: str,
    ) -> StoredNormalizedTextDTO: ...

    async def load_normalized_text(
        self,
        *,
        location: StorageObjectLocationDTO,
        expected_sha256: str | None = None,
    ) -> str: ...

    async def delete(self, *, location: StorageObjectLocationDTO) -> None: ...
