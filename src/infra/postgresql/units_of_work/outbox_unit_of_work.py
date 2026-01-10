from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.outbox_event import OutboxEvent
from src.domain.ports.repositories.ioutbox_repository import IOutboxRepository
from src.domain.ports.system.iclock import IClock
from src.domain.ports.units_of_work.ioutbox_unit_of_work import IOutboxUnitOfWork
from src.infra.postgresql.connection import DBConnectionHandler
from src.infra.postgresql.mappers.interface.imapper import IMapper
from src.infra.postgresql.models import OutboxModel
from src.infra.postgresql.repositories.outbox_repository import OutboxRepository
from src.infra.postgresql.units_of_work.base_unit_of_work import SQLAlchemyUnitOfWork


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