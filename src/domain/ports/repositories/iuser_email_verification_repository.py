from typing import Protocol, Optional
from src.domain.entities.email_verification import EmailVerification
from src.domain.value_objects.user_id import UserId


class IUserEmailVerificationRepository(Protocol):

    async def create_verification_code(self, email_verification: EmailVerification) -> EmailVerification:
        ...


    async def get_by_code(self, code: str) -> Optional[EmailVerification]:
        ...

    async def validate_email_verification(self, email_verification):
        pass

    async def revoke(self, email_verification: EmailVerification) -> None:
        ...

    async def get_by_user_id(self, user_id: UserId) -> Optional[EmailVerification]:
        ...