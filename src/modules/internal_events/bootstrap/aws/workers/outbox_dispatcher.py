from src.shared.config.settings import get_settings
from src.modules.internal_events.infrastructure.messaging.workers.outbox_dispatcher_worker import OutboxDispatcherWorker
from src.modules.internal_events.bootstrap.event_router import get_sqs_event_router
from src.modules.internal_events.bootstrap.units_of_work import get_outbox_unit_of_work
from src.modules.internal_events.bootstrap.strategies import get_exponential_backoff_strategy
from src.shared.infrastructure.system.providers import get_clock

_SETTINGS = get_settings()

def get_outbox_dispatcher_worker() -> OutboxDispatcherWorker:
    return OutboxDispatcherWorker(
        event_router=get_sqs_event_router(),
        uow=get_outbox_unit_of_work(),
        batch_limit=_SETTINGS.BATCH_LIMIT,
        attempts_limit=_SETTINGS.ATTEMPTS_LIMIT,
        system_clock=get_clock(),
        backoff_strategy=get_exponential_backoff_strategy()
    )
