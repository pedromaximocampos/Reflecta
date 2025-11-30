from typing import Optional

from src.domain.entities.email_verification import EmailVerification
from src.domain.entities.user import User
from src.domain.events.email_verification_requested import EmailVerificationRequested
from src.domain.exceptions.custom_exceptions.email_verification_exceptions import EmailVerificationException
from src.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.domain.ports.system.iclock import IClock
from src.domain.ports.system.ihasher_generator import IHasherGenerator
from src.domain.ports.system.iulid_generator import IULIDGenerator
from .iemail_verification_service import  IEmailVerificationService
import secrets
from datetime import timedelta

from ...ports.messaging.iemail_verification_publisher import IEmailVerificationPublisher


class EmailVerificationServiceImpl(IEmailVerificationService):


    def __init__(self, user_email_verification_repository: IUserEmailVerificationRepository, hash_generator: IHasherGenerator,
                 system_clock: IClock, ulid_generator: IULIDGenerator, email_verification_publisher:  IEmailVerificationPublisher)  -> None :
        self.__user_email_verification_repository = user_email_verification_repository
        self.__hash_generator = hash_generator
        self.__clock = system_clock
        self.__ulid_generator = ulid_generator
        self.__email_verification_publisher = email_verification_publisher


    async def issue_for_user(self, user: User) -> tuple[EmailVerification, str]:

        verification, raw = self.__create_email_verification_entity(user)

        created_verification = await self.__user_email_verification_repository.create_verification_code(verification)

        email_verification_event = self.__create_email_verification_event(user, raw)

        await self.__email_verification_publisher.publish(email_verification_event)

        return created_verification, raw

    async def ensure_active_verification_for_user(self, user: User) -> EmailVerification:
        now = self.__clock.now()
        verification: Optional[EmailVerification] = await self.__user_email_verification_repository.get_by_user_id(user.id)

        if not verification:
            await self.issue_for_user(user)
            raise EmailVerificationException("Voce ainda nao esta verificado. Um código de verificação foi enviado para seu email.")

        if verification.is_expired:
            verification.revoke(now)
            await self.__user_email_verification_repository.revoke(verification)
            await self.issue_for_user(user)
            raise EmailVerificationException("Voce ainda nao esta verificado. Um código de verificação foi enviado para seu email.")

        return verification


    def __create_email_verification_entity(self, user: User) -> tuple[EmailVerification, str]:
        raw = secrets.token_urlsafe(32)
        token_hash = self.__hash_generator.generate_hash(raw)

        now = self.__clock.now()
        expires_at = now + timedelta(
            seconds=self.__clock.email_verification_code_expiration_in_seconds()
        )

        verification = EmailVerification(
            id=self.__ulid_generator.generate_ulid(),
            user_id=user.id,
            token_hash=token_hash,
            created_at=now,
            expires_at=expires_at
        )

        return verification, raw


    @staticmethod
    def __create_email_verification_event(user: User, raw_token: str) -> EmailVerificationRequested:
        return EmailVerificationRequested(
            user_id=user.id,
            user_email=user.email,
            raw_code=raw_token,
            user_name=user.username,
        )