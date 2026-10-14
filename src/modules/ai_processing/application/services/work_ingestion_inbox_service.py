from datetime import timedelta

from src.modules.ai_processing.application.exceptions import InboxClaimLostError
from src.modules.ai_processing.application.ports.inbox import IWorkIngestionInbox
from src.modules.ai_processing.domain.ports.unit_of_work import (
    IAIProcessingUnitOfWork,
)
from src.modules.ai_processing.domain.value_objects import InboxClaim
from src.shared.domain.ports.system.iclock import IClock


class WorkIngestionInboxService(IWorkIngestionInbox):
    _FAILURE_MESSAGE = "Work ingestion event processing failed; inspect worker logs."

    def __init__(
        self,
        *,
        uow: IAIProcessingUnitOfWork,
        clock: IClock,
        consumer_name: str,
    ) -> None:
        if not consumer_name.strip():
            raise ValueError("Inbox consumer name must not be empty.")
        self._uow = uow
        self._clock = clock
        self._consumer_name = consumer_name

    async def claim(self, event_id: str, *, lease_seconds: int) -> InboxClaim:
        self._validate_lease_seconds(lease_seconds)
        now = self._clock.now()
        async with self._uow as uow:
            claim = await uow.inbox_event_repository.claim(
                consumer_name=self._consumer_name,
                event_id=event_id,
                now=now,
                lease_expires_at=now + timedelta(seconds=lease_seconds),
            )
            await uow.commit()
            return claim

    async def renew(
        self,
        event_id: str,
        *,
        expected_attempt: int,
        lease_seconds: int,
    ) -> None:
        self._validate_lease_seconds(lease_seconds)
        now = self._clock.now()
        async with self._uow as uow:
            renewed = await uow.inbox_event_repository.renew_claim(
                consumer_name=self._consumer_name,
                event_id=event_id,
                expected_attempt=expected_attempt,
                now=now,
                lease_expires_at=now + timedelta(seconds=lease_seconds),
            )
            if not renewed:
                raise InboxClaimLostError(event_id)
            await uow.commit()

    async def mark_processed(
        self,
        event_id: str,
        *,
        expected_attempt: int,
    ) -> None:
        async with self._uow as uow:
            updated = await uow.inbox_event_repository.mark_processed(
                consumer_name=self._consumer_name,
                event_id=event_id,
                expected_attempt=expected_attempt,
                now=self._clock.now(),
            )
            if not updated:
                raise InboxClaimLostError(event_id)
            await uow.commit()

    async def mark_failed(
        self,
        event_id: str,
        *,
        expected_attempt: int,
        error_code: str,
    ) -> bool:
        async with self._uow as uow:
            updated = await uow.inbox_event_repository.mark_failed(
                consumer_name=self._consumer_name,
                event_id=event_id,
                expected_attempt=expected_attempt,
                now=self._clock.now(),
                error_code=error_code[:128],
                error_message=self._FAILURE_MESSAGE,
            )
            await uow.commit()
            return updated

    @staticmethod
    def _validate_lease_seconds(lease_seconds: int) -> None:
        if lease_seconds <= 0:
            raise ValueError("Inbox lease duration must be positive.")
