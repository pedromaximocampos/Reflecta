from typing import Protocol

from src.modules.notification.application.ports.dto import EmailPasswordResetDTO


class IEmailPasswordResetNotifier(Protocol):
    """Interface for sending password reset notification emails."""

    async def send_email(self, email_password_reset_dto: EmailPasswordResetDTO) -> None:
        """Sends a password reset email to the user.

        Args:
            email_password_reset_dto: Data transfer object containing email details.
        """
        ...