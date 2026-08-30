from typing import Optional
from src.modules.auth.domain.entities.email_verification import EmailVerification
from src.modules.auth.domain.entities.user import User
from src.modules.auth.domain.events.emails.verification_requested import EmailVerificationRequested
from src.modules.auth.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.ihasher_generator import IHasherGenerator
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator
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

        email_verification_event = self.__create_email_verification_event(user, raw, verification)


        return email_verification_event

    async def ensure_or_issue(self, user: User, repo: IUserEmailVerificationRepository) -> Optional[EmailVerificationRequested]:
        now = self.__clock.now()
        verification = await repo.get_active_email_verification_by_user_id(user.id)

        if verification and not verification.is_expired(now):
            return None

        if verification and verification.is_expired(now):
            verification.revoke(now)
            await repo.revoke(verification)

        new_verification, raw = self.__create_email_verification_entity(user)
        await repo.create_verification_code(new_verification)

        return self.__create_email_verification_event(user, raw, new_verification)


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



    def __create_email_verification_event(
        self,
        user: User,
        raw_token: str,
        verification: EmailVerification,
    ) -> EmailVerificationRequested:
        expires_in_minutes = int(
            (verification.expires_at - verification.created_at).total_seconds() // 60
        )

        return EmailVerificationRequested(
            user_id=user.id,
            user_email=user.email,
            raw_code=raw_token,
            expires_in_minutes=expires_in_minutes,
            username=user.username,
            occurred_at=self.__clock.now()
        )
