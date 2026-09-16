from src.modules.internal_events.infrastructure.messaging.routing.event_router import EventRouter
from src.modules.internal_events.bootstrap.aws.publishers import get_emails_sqs_publishers, get_sns_publisher
from src.modules.internal_events.bootstrap.rabbitmq.publishers import (
    get_email_password_reset_publisher,
    get_email_verification_publisher,
)


def get_sqs_event_router() -> EventRouter:
    return EventRouter({
        "emails": get_emails_sqs_publishers()
    })


def get_sns_event_router() -> EventRouter:
    return EventRouter(
        routes={},
        default=get_sns_publisher()
    )


def get_rabbitmq_event_router() -> EventRouter:
    return EventRouter({
        "emails.verification.requested": get_email_verification_publisher(),
        "emails.password_reset.requested": get_email_password_reset_publisher(),
    })
