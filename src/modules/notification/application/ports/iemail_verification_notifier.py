from typing import Protocol

from src.modules.notification.application.ports.dto import EmailVerificationDTO


class IEmailVerificationNotifier(Protocol):

    async def send_email(self, dto: EmailVerificationDTO) -> None:
        """ Envia o email de verificação para o usuário."""
