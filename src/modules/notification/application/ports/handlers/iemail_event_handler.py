from collections.abc import Mapping
from typing import Any, Protocol

from src.modules.notification.domain.value_objects.event_types import EventType


class IEmailEventHandler(Protocol):
    async def handle(self, event_type: EventType, payload: Mapping[str, Any]) -> None:
        """Handle an email event independently from the message broker."""
        ...
