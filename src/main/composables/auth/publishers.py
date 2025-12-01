from src.core.settings import get_settings
from src.infra.messaging.rabbitmq.publishers.email_verification_publisher import EmailVerificationPublisher


_settings = get_settings()

def get_email_verification_publisher() -> EmailVerificationPublisher:
    return EmailVerificationPublisher(_settings.rabbitmq_url, _settings.RABBITMQ_EMAIL_EXCHANGE, _settings.RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY)