from typing import Protocol

from src.modules.ai_processing.domain.value_objects import InboxClaim


class IWorkIngestionInbox(Protocol):
    async def claim(self, event_id: str, *, lease_seconds: int) -> InboxClaim: ...

    async def renew(
        self,
        event_id: str,
        *,
        expected_attempt: int,
        lease_seconds: int,
    ) -> None: ...

    async def mark_processed(
        self,
        event_id: str,
        *,
        expected_attempt: int,
    ) -> None: ...

    async def mark_failed(
        self,
        event_id: str,
        *,
        expected_attempt: int,
        error_code: str,
    ) -> bool: ...
