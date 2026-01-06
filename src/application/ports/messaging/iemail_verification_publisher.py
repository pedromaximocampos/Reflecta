from src.domain.events.emails.verification_requested import EmailVerificationRequested
from typing import Protocol



class IEmailVerificationPublisher(Protocol):


    async def publish(self, event: EmailVerificationRequested) -> None:
        """ Publica o evento de verificação de email solicitado.
        """
        ...

