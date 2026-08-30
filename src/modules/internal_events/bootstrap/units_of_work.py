from src.modules.internal_events.infrastructure.persistence.postgresql.mappers.outbox_mapper import OutboxMapper
from src.modules.internal_events.infrastructure.persistence.postgresql.units_of_work.outbox_unit_of_work import OutboxUnitOfWork
from src.shared.infrastructure.persistence.postgresql.provider import individuum_mvp_provider
from src.shared.infrastructure.system.providers import get_clock


def get_outbox_unit_of_work() -> OutboxUnitOfWork:

    return OutboxUnitOfWork(
        db=individuum_mvp_provider,
        system_clock=get_clock(),
        outbox_mapper=OutboxMapper(),
    )