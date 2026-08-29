import asyncio
from abc import ABC
from typing import Optional

from src.modules.internal_events.application.ports.messaging.ievent_publisher import IEventPublisher
from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent
from src.modules.internal_events.infrastructure.messaging.aws_sqs.clients.sqs_clients import make_sqs_client
from src.modules.internal_events.infrastructure.messaging.aws_sqs.configs.sqs_settings import SQSSettings


class BaseSQSPublisher(IEventPublisher, ABC):   # ABC a classe nao pode ser instanciada, ou mostra que um metodo tem que
                                                # ser implementado ou isso define um contrato claro"

    def __init__(self, sqs_settings: SQSSettings):
        self.__sqs_settings = sqs_settings
        self.__client = make_sqs_client(self.__sqs_settings)

    def _build_message(self, event: OutboxEvent) -> tuple[str, Optional[dict]]:
        return event.payload_json, event.attributes

    def sync_publish(self, event: OutboxEvent) -> None:
        payload, attributes = self._build_message(event)

        kwargs = {
            "QueueUrl": self.__sqs_settings.queue_url,
            "MessageBody": payload,
        }

        if attributes:
            kwargs["MessageAttributes"] = self._to_sqs_attributes(attributes)

        self.__client.send_message(**kwargs)

    def _to_sqs_attributes(self, attrs: dict) -> dict:
        out = {}
        for k, v in attrs.items():
            if v is None:
                continue
            if isinstance(v, (int, float)):
                out[k] = {"DataType": "Number", "StringValue": str(v)}
            else:
                 out[k] = {"DataType": "String", "StringValue": str(v)}
        return out

    async def publish(self, event: OutboxEvent) -> None:
        await asyncio.to_thread(self.sync_publish, event)

