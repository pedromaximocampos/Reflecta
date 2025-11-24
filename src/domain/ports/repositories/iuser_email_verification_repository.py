from typing import Protocol
from src.domain.entities.email_verification import EmailVerification


class IUserEmailVerificationRepository(Protocol):

    async def create_verification_code(self, email_verification: EmailVerification) -> EmailVerification:
        ...