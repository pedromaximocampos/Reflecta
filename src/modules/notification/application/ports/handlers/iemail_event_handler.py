from collections.abc import Mapping
from typing import Any, Protocol

from src.modules.notification.domain.value_objects.emails_event_types import EmailsEventType


class IEmailEventHandler(Protocol):
    async def handle(self, event_type: EmailsEventType, payload: Mapping[str, Any]) -> None:
        """Handle an email event independently from the message broker."""
        ...
