from typing import BinaryIO, Protocol

from src.modules.catalog.application.dto.stored_work_document import (
    StoredWorkDocumentDTO,
)
from src.modules.catalog.domain.value_objects.work_document_location import (
    WorkDocumentLocation,
)


class IWorkDocumentStorage(Protocol):
    async def upload(
        self,
        *,
        object_key: str,
        content: BinaryIO,
        content_type: str,
        size_bytes: int,
    ) -> StoredWorkDocumentDTO: ...

    async def delete(self, *, location: WorkDocumentLocation) -> None: ...

    async def exists(self, *, location: WorkDocumentLocation) -> bool: ...
