from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ai_processing.domain.entities import InboxEvent
from src.modules.ai_processing.domain.ports.repositories import IInboxEventRepository
from src.modules.ai_processing.domain.value_objects import (
    InboxClaim,
    InboxClaimOutcome,
    InboxEventStatus,
)
from src.modules.ai_processing.infrastructure.persistence.postgresql.models import (
    InboxEventModel,
)
from src.shared.infrastructure.persistence.mappers.interface import IMapper


class InboxEventRepository(IInboxEventRepository):
    def __init__(
        self,
        session: AsyncSession,
        mapper: IMapper[InboxEventModel, InboxEvent],
    ) -> None:
        self._session = session
        self._mapper = mapper

    async def claim(
        self,
        *,
        consumer_name: str,
        event_id: str,
        now: datetime,
        lease_expires_at: datetime,
    ) -> InboxClaim:
        new_event = InboxEvent(
            consumer_name=consumer_name,
            event_id=event_id,
            status=InboxEventStatus.PROCESSING,
            attempts=1,
            received_at=now,
            updated_at=now,
            lease_expires_at=lease_expires_at,
        )
        values = self._values(new_event)
        insert_statement = (
            postgresql_insert(InboxEventModel)
            .values(**values)
            .on_conflict_do_nothing(
                index_elements=["consumer_name", "event_id"],
            )
            .returning(InboxEventModel.event_id)
        )
        inserted_event_id = (
            await self._session.execute(insert_statement)
        ).scalar_one_or_none()

        model = await self._get_for_update(consumer_name, event_id)
        if model is None:
            raise RuntimeError("Claimed inbox event could not be reloaded.")
        event = self._mapper.to_entity(model)

        if inserted_event_id is not None:
            return InboxClaim(InboxClaimOutcome.CLAIMED, event.attempts)
        if event.status is InboxEventStatus.PROCESSED:
            return InboxClaim(
                InboxClaimOutcome.ALREADY_PROCESSED,
                event.attempts,
            )
        if event.has_active_lease(now=now):
            return InboxClaim(InboxClaimOutcome.BUSY, event.attempts)

        event.restart_processing(now=now, lease_expires_at=lease_expires_at)
        self._copy_mutable_state(model, event)
        await self._session.flush()
        return InboxClaim(InboxClaimOutcome.CLAIMED, event.attempts)

    async def renew_claim(
        self,
        *,
        consumer_name: str,
        event_id: str,
        expected_attempt: int,
        now: datetime,
        lease_expires_at: datetime,
    ) -> bool:
        if lease_expires_at <= now:
            raise ValueError("Inbox processing lease must expire in the future.")
        statement = (
            update(InboxEventModel)
            .where(
                InboxEventModel.consumer_name == consumer_name,
                InboxEventModel.event_id == event_id,
                InboxEventModel.status == InboxEventStatus.PROCESSING.value,
                InboxEventModel.attempts == expected_attempt,
            )
            .values(updated_at=now, lease_expires_at=lease_expires_at)
            .returning(InboxEventModel.event_id)
        )
        return (await self._session.execute(statement)).scalar_one_or_none() is not None

    async def mark_processed(
        self,
        *,
        consumer_name: str,
        event_id: str,
        expected_attempt: int,
        now: datetime,
    ) -> bool:
        statement = (
            update(InboxEventModel)
            .where(
                InboxEventModel.consumer_name == consumer_name,
                InboxEventModel.event_id == event_id,
                InboxEventModel.status == InboxEventStatus.PROCESSING.value,
                InboxEventModel.attempts == expected_attempt,
            )
            .values(
                status=InboxEventStatus.PROCESSED.value,
                updated_at=now,
                lease_expires_at=None,
                processed_at=now,
                error_code=None,
                error_message=None,
            )
            .returning(InboxEventModel.event_id)
        )
        return (await self._session.execute(statement)).scalar_one_or_none() is not None

    async def mark_failed(
        self,
        *,
        consumer_name: str,
        event_id: str,
        expected_attempt: int,
        now: datetime,
        error_code: str,
        error_message: str,
    ) -> bool:
        if not error_code.strip() or not error_message.strip():
            raise ValueError("Inbox failure code and message must not be empty.")
        statement = (
            update(InboxEventModel)
            .where(
                InboxEventModel.consumer_name == consumer_name,
                InboxEventModel.event_id == event_id,
                InboxEventModel.status == InboxEventStatus.PROCESSING.value,
                InboxEventModel.attempts == expected_attempt,
            )
            .values(
                status=InboxEventStatus.FAILED.value,
                updated_at=now,
                lease_expires_at=None,
                processed_at=None,
                error_code=error_code,
                error_message=error_message,
            )
            .returning(InboxEventModel.event_id)
        )
        return (await self._session.execute(statement)).scalar_one_or_none() is not None

    async def _get_for_update(
        self,
        consumer_name: str,
        event_id: str,
    ) -> InboxEventModel | None:
        result = await self._session.execute(
            select(InboxEventModel)
            .where(
                InboxEventModel.consumer_name == consumer_name,
                InboxEventModel.event_id == event_id,
            )
            .with_for_update()
        )
        return result.scalar_one_or_none()

    @staticmethod
    def _copy_mutable_state(model: InboxEventModel, event: InboxEvent) -> None:
        for name, value in InboxEventRepository._mutable_values(event).items():
            setattr(model, name, value)

    @staticmethod
    def _mutable_values(event: InboxEvent) -> dict[str, object]:
        return {
            "status": event.status.value,
            "attempts": event.attempts,
            "updated_at": event.updated_at,
            "lease_expires_at": event.lease_expires_at,
            "processed_at": event.processed_at,
            "error_code": event.error_code,
            "error_message": event.error_message,
        }

    @classmethod
    def _values(cls, event: InboxEvent) -> dict[str, object]:
        return {
            "consumer_name": event.consumer_name,
            "event_id": event.event_id,
            "received_at": event.received_at,
            **cls._mutable_values(event),
        }
