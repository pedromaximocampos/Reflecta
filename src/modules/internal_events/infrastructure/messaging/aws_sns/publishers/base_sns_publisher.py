import asyncio
from abc import ABC
from typing import Optional

from mypy_boto3_sns import SNSClient

from modules.internal_events.infrastructure.messaging.helpers.aws_pub_helper import AwsPubHelper
from src.modules.internal_events.application.ports.messaging.ievent_publisher import IEventPublisher
from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.infrastructure.messaging.aws_sns.clients.sns_client import make_sns_client
from src.modules.internal_events.infrastructure.messaging.aws_sns.configs.sns_settings import SNSSettings


class BaseSnsPublisher(IEventPublisher, ABC):
    def __init__(self, sns_configs: SNSSettings) -> None:
        self.sns_settings = sns_configs
        self.client: SNSClient = make_sns_client(sns_configs)

    async def publish(self, event: OutboxEvent) -> None:
        await asyncio.to_thread(self.sync_publish, event)


    def sync_publish(self, event: OutboxEvent) -> None:
        payload, attributes = AwsPubHelper.build_message(event)

        message_attributes = AwsPubHelper.to_attributes(attributes) if attributes else None

        self.client.publish(
            TopicArn=self.sns_settings.sns_arn,
            Message=payload,
            MessageAttributes=message_attributes
        )

