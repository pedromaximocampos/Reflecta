from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.internal_events.infrastructure.persistence.postgresql.mappers.outbox_mapper import (
    OutboxMapper,
)
from src.modules.internal_events.infrastructure.persistence.postgresql.repositories.outbox_repository import (
    OutboxRepository,
)
from src.modules.internal_events.public import IOutboxRepository
from src.modules.sharing.domain.ports import (
    IProfessionalActivityRepository,
    ISharingUnitOfWork,
)
from src.modules.sharing.infrastructure.persistence.postgresql.mappers import (
    ProfessionalActivityMapper,
)
from src.modules.sharing.infrastructure.persistence.postgresql.repositories import (
    ProfessionalActivityRepository,
)
from src.shared.domain.ports.system.iclock import IClock
from src.shared.infrastructure.persistence.postgresql.connection import DBConnectionHandler
from src.shared.infrastructure.persistence.postgresql.units_of_work.base_unit_of_work import (
    SQLAlchemyUnitOfWork,
)


class SharingUnitOfWork(SQLAlchemyUnitOfWork, ISharingUnitOfWork):
    def __init__(self, db: DBConnectionHandler, clock: IClock) -> None:
        super().__init__(db)
        self._clock = clock
        self._activity_repository: IProfessionalActivityRepository | None = None
        self._outbox_repository: IOutboxRepository | None = None

    @property
    def activity_repository(self) -> IProfessionalActivityRepository:
        if self._activity_repository is None:
            raise RuntimeError("Unit of work is not active.")
        return self._activity_repository

    @property
    def outbox_repository(self) -> IOutboxRepository:
        if self._outbox_repository is None:
            raise RuntimeError("Unit of work is not active.")
        return self._outbox_repository

    async def _init_repositories(self, session: AsyncSession) -> None:
        self._activity_repository = ProfessionalActivityRepository(
            session,
            ProfessionalActivityMapper(),
        )
        self._outbox_repository = OutboxRepository(
            session,
            OutboxMapper(),
            self._clock,
        )

    def _clear_repositories(self) -> None:
        self._activity_repository = None
        self._outbox_repository = None

