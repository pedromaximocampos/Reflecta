from src.modules.internal_events.infrastructure.messaging.routing.event_router import EventRouter
from src.modules.internal_events.bootstrap.aws.publishers import get_emails_sqs_publishers


def get_event_router() -> EventRouter:
    return EventRouter({
        "emails": get_emails_sqs_publishers()
    })