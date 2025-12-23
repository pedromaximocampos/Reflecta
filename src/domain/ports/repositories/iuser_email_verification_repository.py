from typing import Protocol, Optional
from src.domain.entities.email_verification import EmailVerification
from src.domain.value_objects.user_id import UserId


class IUserEmailVerificationRepository(Protocol):

    async def create_verification_code(self, email_verification: EmailVerification) -> EmailVerification:
        ...


    async def get_by_code(self, hashed_code: str) -> Optional[EmailVerification]:
        ...

    async def mark_as_verified(self, email_verification: EmailVerification) -> None:
        ...

    async def revoke(self, email_verification: EmailVerification) -> None:
        ...

    async def get_active_email_verification_by_user_id(self, user_id: UserId) -> Optional[EmailVerification]:
        ...