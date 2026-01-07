from src.domain.entities.outbox_event import OutboxEvent
from src.domain.ports.repositories.ioutbox_repository import IOutboxRepository
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.postgresql.mappers.interface.imapper import IMapper
from src.infra.postgresql.models.outbox_model import OutboxModel


class OutboxRepository(IOutboxRepository):

    def __init__(self, session: AsyncSession, outbox_mapper: IMapper[OutboxModel, OutboxEvent]) -> None:
        self._session = session
        self._mapper = outbox_mapper

    async def add_event(self, event: OutboxEvent) -> None:
        return await super().add_event(event)