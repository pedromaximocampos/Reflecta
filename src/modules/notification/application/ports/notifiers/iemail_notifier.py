from typing import Protocol

from src.modules.notification.application.ports.notifiers.dto import EmailDTO


class IEmailNotifier(Protocol):
    async def send_email(self, dto: EmailDTO) -> None:
        """Send an email notification."""
        ...
