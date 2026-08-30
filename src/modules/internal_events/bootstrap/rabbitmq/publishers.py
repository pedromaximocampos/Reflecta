from src.modules.internal_events.infrastructure.messaging.rabbitmq.publishers.email_reset_password_publisher import EmailResetPasswordPublisher
from src.modules.internal_events.infrastructure.messaging.rabbitmq.publishers.email_verification_publisher import EmailVerificationPublisher
from src.modules.internal_events.bootstrap.rabbitmq.rabbit_mq import get_email_verification_publisher_config, \
    get_password_reset_publisher_config, get_email_verification_consumer_config, get_password_reset_consumer_config


def get_email_verification_publisher() -> EmailVerificationPublisher:
    return EmailVerificationPublisher(
        get_email_verification_publisher_config(),
        get_email_verification_consumer_config(),
    )


def get_email_password_reset_publisher() -> EmailResetPasswordPublisher:
    return EmailResetPasswordPublisher(
        get_password_reset_publisher_config(),
        get_password_reset_consumer_config(),
    )
