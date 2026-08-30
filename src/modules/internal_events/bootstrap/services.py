from src.modules.internal_events.application.services.outbox_service_impl import OutboxServiceImpl
from src.shared.infrastructure.system.providers import get_clock, get_ulid_generator


def get_outbox_service() -> OutboxServiceImpl:
    return OutboxServiceImpl(
        system_clock=get_clock(),
        ulid_generator=get_ulid_generator()
    )