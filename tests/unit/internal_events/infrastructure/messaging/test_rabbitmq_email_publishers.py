from datetime import datetime, timezone

from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.domain.value_objects.event_type import EventType
from src.modules.internal_events.infrastructure.messaging.rabbitmq.configs.settings import (
    RabbitMQConsumerConfig,
    RabbitMQPublisherConfig,
)
from src.modules.internal_events.infrastructure.messaging.rabbitmq.publishers.email_reset_password_publisher import (
    EmailResetPasswordPublisher,
)
from src.modules.internal_events.infrastructure.messaging.rabbitmq.publishers.email_verification_publisher import (
    EmailVerificationPublisher,
)


def _publisher_config(routing_key: str) -> RabbitMQPublisherConfig:
    return RabbitMQPublisherConfig(
        url="amqp://guest:guest@localhost:5672/",
        exchange_name="email",
        routing_key=routing_key,
        queue_name=routing_key,
        frontend_base_url="http://localhost:8000/",
    )


def _topology_config(routing_key: str) -> RabbitMQConsumerConfig:
    return RabbitMQConsumerConfig(
        url="amqp://guest:guest@localhost:5672/",
        host="localhost",
        port=5672,
        user="guest",
        password="guest",
        virtual_host="/",
        queue_name=routing_key,
        exchange_name="email",
        routing_key=routing_key,
        retry_queue_name=f"{routing_key}.retry",
        retry_routing_key=f"{routing_key}.retry",
        dlx_queue_name=f"{routing_key}.dlq",
        dlx_routing_key=f"{routing_key}.dlq",
        dlx_exchange="email.dlx",
        max_retries=5,
        frontend_base_url="http://localhost:8000/",
    )


def _event(event_type: str) -> OutboxEvent:
    now = datetime(2026, 8, 30, tzinfo=timezone.utc)
    return OutboxEvent(
        id="01TESTOUTBOXEVENT00000000",
        event_type=EventType(event_type),
        payload={"raw_code": "test-code"},
        event_occurred_at=now,
        created_at=now,
    )


def test_email_verification_publisher_keeps_broker_neutral_payload() -> None:
    routing_key = "email.verification"
    publisher = EmailVerificationPublisher(
        _publisher_config(routing_key),
        _topology_config(routing_key),
    )

    payload, _ = publisher._build_message(
        _event("emails.verification.requested")
    )

    assert payload == {"raw_code": "test-code"}


def test_password_reset_publisher_keeps_broker_neutral_payload() -> None:
    routing_key = "password.reset"
    publisher = EmailResetPasswordPublisher(
        _publisher_config(routing_key),
        _topology_config(routing_key),
    )

    payload, _ = publisher._build_message(
        _event("emails.password_reset.requested")
    )

    assert payload == {"raw_code": "test-code"}
