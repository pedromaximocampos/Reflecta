from typing import Protocol, runtime_checkable

from src.application.ports.emails.dto import EmailVerificationDTO
from src.domain.events.email_verification_requested import EmailVerificationRequested

class IEmailVerificationNotifier(Protocol):

    async def send_email(self, dto: EmailVerificationDTO) -> None:
        """ Envia o email de verificação para o usuário."""
