from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.domain.ports.repositories.ioutbox_repository import IOutboxRepository
from src.shared.domain.ports.system.iclock import IClock
from src.modules.internal_events.domain.ports.units_of_work.ioutbox_unit_of_work import IOutboxUnitOfWork
from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler
from src.shared.infrastructure.persistence.mappers.interface import IMapper
from src.modules.internal_events.infrastructure.persistence.postgresql.models import OutboxModel
from src.modules.internal_events.infrastructure.persistence.postgresql.repositories.outbox_repository import OutboxRepository
from src.shared.infrastructure.persistence.postgresql.units_of_work.base_unit_of_work import SQLAlchemyUnitOfWork


class OutboxUnitOfWork(SQLAlchemyUnitOfWork, IOutboxUnitOfWork):


    @property
    def outbox_repository(self) -> IOutboxRepository:
        assert self.__outbox_repository is not None
        return  self.__outbox_repository

    def __init__(self, db: DBConnectionHandler, system_clock: IClock, outbox_mapper: IMapper[OutboxModel, OutboxEvent]) -> None:
        super().__init__(db)
        self.__clock = system_clock
        self.__outbox_mapper = outbox_mapper
        self.__outbox_repository: Optional[OutboxRepository] = None


    async def _init_repositories(self, session: AsyncSession) -> None:
        self.__outbox_repository = OutboxRepository(session, self.__outbox_mapper, self.__clock)

    def _clear_repositories(self) -> None:
        self.__outbox_repository = None
