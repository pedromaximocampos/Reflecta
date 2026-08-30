from datetime import datetime

from sqlalchemy import select, update, or_

from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.domain.ports.repositories.ioutbox_repository import IOutboxRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.ports.system.iclock import IClock
from src.modules.internal_events.domain.value_objects.outbox_status import OutboxStatus
from src.shared.infrastructure.persistence.postgresql.mappers.interface.imapper import IMapper
from src.modules.internal_events.infrastructure.persistence.postgresql.models.outbox_model import OutboxModel


class OutboxRepository(IOutboxRepository):

    def __init__(self, session: AsyncSession, outbox_mapper: IMapper[OutboxModel, OutboxEvent], system_clock: IClock) -> None:
        self._session = session
        self._mapper = outbox_mapper
        self.__clock = system_clock

    async def add_event(self, event: OutboxEvent) -> None:
        outbox_model  =  self._mapper.to_model(event)

        self._session.add(outbox_model)
        await self._session.flush()

    async def claim_pending(self, batch_limit: int, attempts_limit: int) -> list[OutboxEvent]:
        now = self.__clock.now()
        query = (
            select(OutboxModel)
            .where(OutboxModel.status.in_([OutboxStatus.PENDING, OutboxStatus.FAILED]),
                   OutboxModel.attempts < attempts_limit,
                   or_(
                       OutboxModel.next_attempt_at.is_(None),
                       OutboxModel.next_attempt_at < now
                   ))
            .order_by(OutboxModel.created_at)
            .limit(batch_limit)
            .with_for_update(skip_locked=True)
        )

        rows = (await self._session.execute(query)).scalars().all()

        if not rows:
            return []

        for row in rows:
            row.status = OutboxStatus.PROCESSING
            row.attempts += 1

        await self._session.flush()

        return [self._mapper.to_entity(event) for event in rows]

    async def mark_sent(self, event: OutboxEvent) -> None:
        query = (
            update(OutboxModel)
            .where(OutboxModel.id == event.id)
            .values(status=OutboxStatus.SENT, sent_at=event.sent_at)
        )
        await self._session.execute(query)

    async def mark_failed(self, event: OutboxEvent) -> None:
        query = (
            update(OutboxModel)
            .where(OutboxModel.id == event.id)
            .values(status=OutboxStatus.FAILED, last_error=event.last_error, failed_at=event.failed_at, next_attempt_at=event.next_attempt_at)
        )

        await self._session.execute(query)