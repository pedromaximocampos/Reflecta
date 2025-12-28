from datetime import datetime
from typing import Optional

from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from .dto import VerifyEmailOutputDTO
from src.domain.entities.email_verification import EmailVerification
from src.domain.entities.user import User
from src.domain.exceptions.custom_exceptions.email_verification_exceptions import EmailVerificationException
from src.domain.exceptions.custom_exceptions.user_custom_exceptions import UserNotFoundError
from src.domain.ports.system.iclock import IClock
from src.domain.ports.system.ihasher_generator import IHasherGenerator
from .iverify_email_verification import IVerifyEmailVerification
from ...services.email_verification.iemail_verification_service import IEmailVerificationService


class VerifyEmailVerificationUseCaseImpl(IVerifyEmailVerification):


    def __init__(self, auth_unit_of_work: IAuthUnitOfWork, hasher_generator: IHasherGenerator,
                 email_verification_service: IEmailVerificationService, system_clock: IClock) -> None:
        self.__auth_unit_of_worker = auth_unit_of_work
        self.__hasher_generator = hasher_generator
        self.__email_verification_service = email_verification_service
        self.__system_clock = system_clock

    async def execute(self, raw_code: str) -> VerifyEmailOutputDTO:

        async with self.__auth_unit_of_worker as uow:
            email_verification = await self.__get_email_verification_by_code(raw_code, uow)
            user = await self.__get_user_from_email_verification(email_verification, uow)

            if email_verification.is_revoked:
                raise EmailVerificationException("Verification code is not active/valid.")

            if email_verification.is_verified:
                return VerifyEmailOutputDTO(
                    success=True,
                    message="Email already verified.",
                )

            now = self.__system_clock.now()

            if email_verification.is_expired(now):
                await self.__revoke_email_verification(email_verification, now, uow)
                await self.__email_verification_service.issue_for_user(user, uow)
                await uow.commit()

                return VerifyEmailOutputDTO(success=False, message="Verification code expired. We sent you a new verification email.")

            await self.__update_user_and_email_verification(user, email_verification, now, uow)

            await uow.commit()

            return VerifyEmailOutputDTO(
                success=True,
                message="Email verified successfully.",
            )

    @staticmethod
    async def __revoke_email_verification(email_verification: EmailVerification, revoked_at: datetime, uow: IAuthUnitOfWork) -> None:
        email_verification.revoke(revoked_at)
        await uow.user_email_verification_repository.revoke(email_verification)

    @staticmethod
    async def __get_user_from_email_verification(email_verification: EmailVerification, uow: IAuthUnitOfWork) -> User:
        user: Optional[User] = await uow.users_repository.find_by_id(email_verification.user_id)

        if not user:
            raise UserNotFoundError()

        return user

    async def __get_email_verification_by_code(self, raw_code: str, uow: IAuthUnitOfWork) -> EmailVerification:
        hashed_code = self.__hasher_generator.generate_hash(raw_code)

        email_verification: Optional[EmailVerification] = await uow.user_email_verification_repository.get_by_code(hashed_code)

        if not email_verification:
            raise EmailVerificationException()

        return email_verification

    @staticmethod
    async def __update_user_and_email_verification(user: User, email_verification: EmailVerification, updated_at: datetime,
                                                   uow: IAuthUnitOfWork) -> None:
        user.mark_email_as_verified(updated_at)
        email_verification.verify(updated_at)

        await uow.users_repository.verify_email(user)
        await uow.user_email_verification_repository.mark_as_verified(email_verification)