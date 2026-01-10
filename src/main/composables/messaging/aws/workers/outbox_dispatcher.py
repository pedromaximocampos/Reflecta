from src.main.composables.shared.settings import _SETTINGS
from src.infra.messaging.workers.publishers.base_sqs_publisher_worker import BaseSqsPublisher
from src.main.composables.messaging.event_router import get_event_router
from src.main.composables.messaging.units_of_work import get_outbox_unit_of_work
from src.main.composables.shared.strategies import get_exponential_backoff_strategy
from src.main.composables.shared.system import get_clock


def get_outbox_dispatcher_worker() -> BaseSqsPublisher:
    return BaseSqsPublisher(
        event_router=get_event_router(),
        uow=get_outbox_unit_of_work(),
        batch_limit=_SETTINGS.BATCH_LIMIT,
        attempts_limit=_SETTINGS.ATTEMPTS_LIMIT,
        system_clock=get_clock(),
        backoff_strategy=get_exponential_backoff_strategy()
    )