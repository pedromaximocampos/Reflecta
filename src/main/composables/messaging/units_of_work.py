from src.infra.postgresql.mappers.outbox_mapper import OutboxMapper
from src.infra.postgresql.units_of_work.outbox_unit_of_work import OutboxUnitOfWork
from src.infra.postgresql.provider import individuum_mvp_provider
from src.main.composables.shared.system import get_clock


def get_outbox_unit_of_work() -> OutboxUnitOfWork:

    return OutboxUnitOfWork(
        db=individuum_mvp_provider,
        system_clock=get_clock(),
        outbox_mapper=OutboxMapper(),
    )