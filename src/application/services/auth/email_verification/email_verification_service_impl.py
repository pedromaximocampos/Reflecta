from typing import Optional
from src.domain.entities.email_verification import EmailVerification
from src.domain.entities.user import User
from src.domain.events.emails.verification_requested import EmailVerificationRequested
from src.domain.exceptions.custom_exceptions.email_verification_exceptions import EmailVerificationException
from src.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.domain.ports.system.iclock import IClock
from src.domain.ports.system.ihasher_generator import IHasherGenerator
from src.domain.ports.system.iulid_generator import IULIDGenerator
from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from .iemail_verification_service import  IEmailVerificationService
import secrets
from datetime import timedelta




class EmailVerificationServiceImpl(IEmailVerificationService):


    def __init__(self, hash_generator: IHasherGenerator,system_clock: IClock, ulid_generator: IULIDGenerator)  -> None :
        self.__hash_generator = hash_generator
        self.__clock = system_clock
        self.__ulid_generator = ulid_generator


    async def create_email_verification_event(self, user: User, user_email_repo: IUserEmailVerificationRepository) -> EmailVerificationRequested:

        verification, raw = self.__create_email_verification_entity(user)

        created_verification = await user_email_repo.create_verification_code(verification)

        email_verification_event = self.__create_email_verification_event(user, raw)


        return email_verification_event

    async def ensure_or_issue(self, user: User, repo: IUserEmailVerificationRepository) -> Optional[EmailVerificationRequested]:
        now = self.__clock.now()
        verification = await repo.get_active_email_verification_by_user_id(user.id)

        if verification and not verification.is_expired:
            return None

        if verification and verification.is_expired:
            verification.revoke(now)
            await repo.revoke(verification)

        new_verification, raw = self.__create_email_verification_entity(user)
        await repo.create_verification_code(new_verification)

        return self.__create_email_verification_event(user, raw)


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



    def __create_email_verification_event(self,user: User, raw_token: str) -> EmailVerificationRequested:
        return EmailVerificationRequested(
            user_id=user.id,
            user_email=user.email,
            raw_code=raw_token,
            username=user.username,
            occurred_at=self.__clock.now()
        )