from datetime import datetime

from sqlalchemy import select, update


from src.domain.entities.outbox_event import OutboxEvent
from src.domain.ports.repositories.ioutbox_repository import IOutboxRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.value_objects.outbox_status import OutboxStatus
from src.infra.postgresql.mappers.interface.imapper import IMapper
from src.infra.postgresql.models.outbox_model import OutboxModel


class OutboxRepository(IOutboxRepository):

    def __init__(self, session: AsyncSession, outbox_mapper: IMapper[OutboxModel, OutboxEvent]) -> None:
        self._session = session
        self._mapper = outbox_mapper

    async def add_event(self, event: OutboxEvent) -> None:
        outbox_model  =  self._mapper.to_model(event)

        self._session.add(outbox_model)
        await self._session.flush()

    async def list_pending(self, limit: int) -> list[OutboxEvent]:
        query = (
            select(OutboxModel)
            .where(OutboxModel.status == OutboxStatus.PENDING)
            .order_by(OutboxEvent.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )

        result = (await self._session.execute(query)).scalars().all()

        return [self._mapper.to_entity(event) for event in result]

    async def mark_sent(self, event_id: int, now: datetime) -> None:
        query = (
            update(OutboxModel)
            .where(OutboxModel.id == event_id)
            .values(status=OutboxStatus.SENT, sent_at=now)
        )
        await self._session.execute(query)

    async def mark_failed(self, event_id: int, error: str) -> None:
        query = (
            update(OutboxModel)
            .where(OutboxModel.id == event_id)
            .values(status=OutboxStatus.FAILED, last_error=error)
        )

        await self._session.execute(query)