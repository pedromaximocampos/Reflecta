from datetime import datetime
from typing import Optional
from .dto import VerifyEmailOutputDTO
from src.domain.entities.email_verification import EmailVerification
from src.domain.entities.user import User
from src.domain.exceptions.custom_exceptions.email_verification_exceptions import EmailVerificationException
from src.domain.exceptions.custom_exceptions.user_custom_exceptions import UserNotFoundError
from src.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.ports.system.iclock import IClock
from src.domain.ports.system.ihasher_generator import IHasherGenerator
from .iverify_email_verification import IVerifyEmailVerification
from ...services.email_verification.iemail_verification_service import IEmailVerificationService


class VerifyEmailVerificationUseCaseImpl(IVerifyEmailVerification):


    def __init__(self, user_email_verification_repository: IUserEmailVerificationRepository, hasher_generator: IHasherGenerator,
                 email_verification_service: IEmailVerificationService, user_repository: IUserRepository, system_clock: IClock) -> None:
        self.__user_email_verification_repository = user_email_verification_repository
        self.__hasher_generator = hasher_generator
        self.__email_verification_service = email_verification_service
        self.__user_repository = user_repository
        self.__system_clock = system_clock

    async def execute(self, raw_code: str) -> VerifyEmailOutputDTO:
        email_verification = await self.__get_email_verification_by_code(raw_code)
        user = await self.__get_user_from_email_verification(email_verification)

        if email_verification.is_revoked:
            raise EmailVerificationException("Este código de verificação não é mais válido.")

        if email_verification.is_verified:
            return VerifyEmailOutputDTO(
                success=True,
                message="Este email já havia sido verificado.",
            )

        now = self.__system_clock.now()

        if email_verification.is_expired:
            await self.__revoke_email_verification(email_verification, now)
            await self.__email_verification_service.issue_for_user(user)

            raise EmailVerificationException(
                "Código de verificação expirado. Um novo código foi enviado para seu email."
            )

        await self.__update_user_and_email_verification(user, email_verification, now)

        return VerifyEmailOutputDTO(
            success=True,
            message="Email verificado com sucesso.",
        )


    async def __revoke_email_verification(self, email_verification: EmailVerification, revoked_at: datetime) -> None:
        email_verification.revoke(revoked_at)
        await self.__user_email_verification_repository.revoke(email_verification)


    async def __get_user_from_email_verification(self, email_verification: EmailVerification) -> User:
        user: Optional[User] = await self.__user_repository.find_by_id(email_verification.user_id)

        if not user:
            raise UserNotFoundError("Não foi possível localizar o usuário associado a esta verificação.")

        return user

    async def __get_email_verification_by_code(self, raw_code: str) -> Optional[EmailVerification]:
        hashed_code = self.__hasher_generator.generate_hash(raw_code)

        email_verification:  Optional[EmailVerification] = await self.__user_email_verification_repository.get_by_code(hashed_code)

        if not email_verification:
            raise EmailVerificationException("Código de verificação inválido.")

        return email_verification

    async def __update_user_and_email_verification(self, user: User, email_verification: EmailVerification, updated_at: datetime) -> None:
        user.mark_email_as_verified(updated_at)
        email_verification.verify(updated_at)

        await self.__user_repository.verify_email(user)
        await self.__user_email_verification_repository.validate_email_verification(email_verification)