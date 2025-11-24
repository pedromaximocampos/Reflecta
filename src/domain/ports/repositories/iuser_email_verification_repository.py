from abc import ABC, abstractmethod

from src.domain.entities.email_verification import EmailVerification


class IUserEmailVerificationRepository(ABC):

    @abstractmethod
    async def create_verification_code(self, email_verification: EmailVerification) -> None:
        ...