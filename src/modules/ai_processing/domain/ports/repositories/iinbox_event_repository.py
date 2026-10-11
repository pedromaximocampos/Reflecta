from datetime import datetime
from typing import Protocol

from src.modules.ai_processing.domain.value_objects import InboxClaim


class IInboxEventRepository(Protocol):
    async def claim(
        self,
        *,
        consumer_name: str,
        event_id: str,
        now: datetime,
        lease_expires_at: datetime,
    ) -> InboxClaim: ...

    async def renew_claim(
        self,
        *,
        consumer_name: str,
        event_id: str,
        expected_attempt: int,
        now: datetime,
        lease_expires_at: datetime,
    ) -> bool: ...

    async def mark_processed(
        self,
        *,
        consumer_name: str,
        event_id: str,
        expected_attempt: int,
        now: datetime,
    ) -> bool: ...

    async def mark_failed(
        self,
        *,
        consumer_name: str,
        event_id: str,
        expected_attempt: int,
        now: datetime,
        error_code: str,
        error_message: str,
    ) -> bool: ...
