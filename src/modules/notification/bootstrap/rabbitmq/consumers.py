from src.modules.notification.infrastructure.messaging.rabbitmq.consumers.email_reset_password_consumer_worker import EmailPasswordResetConsumerWorker
from src.modules.notification.infrastructure.messaging.rabbitmq.consumers.email_verification_consumer_worker import EmailVerificationConsumerWorker
from src.modules.notification.bootstrap.handlers import get_email_event_handler
from src.modules.internal_events.bootstrap.rabbitmq.rabbit_mq import get_email_verification_consumer_config, \
    get_password_reset_consumer_config


# ---------- WORKERS ----------

def get_email_verification_consumer_worker() -> EmailVerificationConsumerWorker:

    return EmailVerificationConsumerWorker(
        consumer_config=get_email_verification_consumer_config(),
        email_event_handler=get_email_event_handler(),
    )


def get_password_reset_consumer_worker() -> EmailPasswordResetConsumerWorker:


    return EmailPasswordResetConsumerWorker(
        consumer_config=get_password_reset_consumer_config(),
        email_event_handler=get_email_event_handler(),
    )
