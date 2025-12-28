from src.core.settings import get_settings
from src.infra.messaging.rabbitmq.publishers.email_reset_password_publisher import EmailResetPasswordPublisher
from src.infra.messaging.rabbitmq.publishers.email_verification_publisher import EmailVerificationPublisher
from src.main.composables.shared.rabbit_mq import get_email_verification_publisher_config, \
    get_password_reset_publisher_config

_settings = get_settings()

def get_email_verification_publisher() -> EmailVerificationPublisher:
    return EmailVerificationPublisher(get_email_verification_publisher_config())


def get_email_password_reset_publisher() -> EmailResetPasswordPublisher:
    return EmailResetPasswordPublisher(get_password_reset_publisher_config())