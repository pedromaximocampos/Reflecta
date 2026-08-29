from src.core.settings import get_settings
from src.modules.internal_events.infrastructure.messaging.rabbitmq.configs.settings import RabbitMQConsumerConfig, RabbitMQPublisherConfig

_settings = get_settings()


# =========================
# CONSUMER CONFIGS
# =========================

def get_email_verification_consumer_config() -> RabbitMQConsumerConfig:
    return RabbitMQConsumerConfig(
        url=_settings.RABBITMQ_URL,

        host=_settings.RABBITMQ_HOST,
        port=_settings.RABBITMQ_PORT,
        user=_settings.RABBITMQ_USER,
        password=_settings.RABBITMQ_PASSWORD,
        virtual_host=_settings.RABBITMQ_VIRTUAL_HOST,

        queue_name=_settings.RABBITMQ_EMAIL_VERIFICATION_QUEUE,
        exchange_name=_settings.RABBITMQ_EMAIL_EXCHANGE,
        routing_key=_settings.RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY,

        retry_queue_name=_settings.RABBITMQ_EMAIL_VERIFICATION_RETRY_QUEUE,
        retry_routing_key=_settings.RABBITMQ_EMAIL_VERIFICATION_RETRY_ROUTING_KEY,

        dlx_queue_name=_settings.RABBITMQ_EMAIL_VERIFICATION_DLX_QUEUE,
        dlx_routing_key=_settings.RABBITMQ_EMAIL_VERIFICATION_DLX_ROUTING_KEY,
        dlx_exchange=_settings.RABBITMQ_EMAIL_DLX_EXCHANGE,

        max_retries=_settings.RABBITMQ_MAX_RETRIES,
        frontend_base_url=_settings.FRONT_END_DOMAIN,
        ssl =_settings.RABBITMQ_USE_SSL,
    )


def get_password_reset_consumer_config() -> RabbitMQConsumerConfig:
    return RabbitMQConsumerConfig(
        url=_settings.RABBITMQ_URL,

        host=_settings.RABBITMQ_HOST,
        port=_settings.RABBITMQ_PORT,
        user=_settings.RABBITMQ_USER,
        password=_settings.RABBITMQ_PASSWORD,
        virtual_host=_settings.RABBITMQ_VIRTUAL_HOST,

        queue_name=_settings.RABBITMQ_PASSWORD_RESET_QUEUE,
        exchange_name=_settings.RABBITMQ_EMAIL_EXCHANGE,
        routing_key=_settings.RABBITMQ_PASSWORD_RESET_ROUTING_KEY,

        retry_queue_name=_settings.RABBITMQ_PASSWORD_RESET_RETRY_QUEUE,
        retry_routing_key=_settings.RABBITMQ_PASSWORD_RESET_RETRY_ROUTING_KEY,

        dlx_queue_name=_settings.RABBITMQ_PASSWORD_RESET_DLX_QUEUE,
        dlx_routing_key=_settings.RABBITMQ_PASSWORD_RESET_DLX_ROUTING_KEY,
        dlx_exchange=_settings.RABBITMQ_EMAIL_DLX_EXCHANGE,

        max_retries=_settings.RABBITMQ_MAX_RETRIES,
        frontend_base_url=_settings.FRONT_END_DOMAIN,
        ssl=_settings.RABBITMQ_USE_SSL,
    )


# =========================
# PUBLISHER CONFIGS
# =========================

def get_email_verification_publisher_config() -> RabbitMQPublisherConfig:
    return RabbitMQPublisherConfig(
        url=_settings.RABBITMQ_URL,

        exchange_name=_settings.RABBITMQ_EMAIL_EXCHANGE,
        routing_key=_settings.RABBITMQ_EMAIL_VERIFICATION_ROUTING_KEY,
        queue_name=_settings.RABBITMQ_EMAIL_VERIFICATION_QUEUE,

        frontend_base_url=_settings.FRONT_END_DOMAIN,
    )


def get_password_reset_publisher_config() -> RabbitMQPublisherConfig:
    return RabbitMQPublisherConfig(
        url=_settings.RABBITMQ_URL,

        exchange_name=_settings.RABBITMQ_EMAIL_EXCHANGE,
        routing_key=_settings.RABBITMQ_PASSWORD_RESET_ROUTING_KEY,
        queue_name=_settings.RABBITMQ_PASSWORD_RESET_QUEUE,

        frontend_base_url=_settings.FRONT_END_DOMAIN,
    )
