from src.modules.internal_events.bootstrap.event_router import get_rabbitmq_event_router
from src.modules.internal_events.bootstrap.strategies import get_exponential_backoff_strategy
from src.modules.internal_events.bootstrap.units_of_work import get_outbox_unit_of_work
from src.modules.internal_events.infrastructure.messaging.workers.outbox_dispatcher_worker import OutboxDispatcherWorker
from src.shared.config.settings import get_settings
from src.shared.infrastructure.system.providers import get_clock


def get_rabbitmq_outbox_dispatcher_worker() -> OutboxDispatcherWorker:
    settings = get_settings()
    return OutboxDispatcherWorker(
        event_router=get_rabbitmq_event_router(),
        uow=get_outbox_unit_of_work(),
        batch_limit=settings.BATCH_LIMIT,
        attempts_limit=settings.ATTEMPTS_LIMIT,
        system_clock=get_clock(),
        backoff_strategy=get_exponential_backoff_strategy(),
    )
