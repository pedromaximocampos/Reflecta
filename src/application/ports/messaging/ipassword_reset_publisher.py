from typing import Protocol

from src.domain.events.emails.password_reset_requested import PasswordResetRequested


class IPasswordResetPublisher(Protocol):


    async def publish_password_reset_requested(self, password_reset_event: PasswordResetRequested) -> None:
        ...
