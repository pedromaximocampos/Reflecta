from typing import Optional

from src.modules.internal_events.domain.entities.outbox_event import OutboxEvent


class AwsPubHelper:

    @staticmethod
    def build_message(event: OutboxEvent) -> tuple[str, Optional[dict]]:
        return event.payload_json, event.attributes


    @staticmethod
    def to_attributes(attrs: dict) -> dict[str, str]:
        out = {}
        for k, v in attrs.items():
            if v is None:
                continue
            if isinstance(v, (int, float)):
                out[k] = {"DataType": "Number", "StringValue": str(v)}
            else:
                out[k] = {"DataType": "String", "StringValue": str(v)}
        return out