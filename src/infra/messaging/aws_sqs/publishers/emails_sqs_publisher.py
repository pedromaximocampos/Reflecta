import json

from src.application.ports.messaging.ievent_publisher import IEventPublisher
from src.domain.entities.outbox_event import OutboxEvent
from src.infra.messaging.aws_sqs.clients.sqs_clients import make_sqs_client
from src.infra.messaging.aws_sqs.configs.sqs_settings import SQSSettings
from src.infra.messaging.aws_sqs.publishers.base_sqs_publisher import BaseSQSPublisher


class EmailSQSPublisher(BaseSQSPublisher):
    pass

