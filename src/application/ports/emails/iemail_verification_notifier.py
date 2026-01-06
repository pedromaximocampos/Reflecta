from typing import Protocol

from src.application.ports.emails.dto import EmailVerificationDTO


class IEmailVerificationNotifier(Protocol):

    async def send_email(self, dto: EmailVerificationDTO) -> None:
        """ Envia o email de verificação para o usuário."""
