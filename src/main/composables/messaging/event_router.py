from src.infra.messaging.routing.event_router import EventRouter
from src.main.composables.messaging.aws.publishers import get_emails_sqs_publishers


def get_event_router() -> EventRouter:
    return EventRouter({
        "emails": get_emails_sqs_publishers()
    })