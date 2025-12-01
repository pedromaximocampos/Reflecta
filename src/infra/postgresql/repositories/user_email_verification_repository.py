from typing import Optional

from src.domain.value_objects.user_id import UserId
from src.infra.postgresql.models import UserEmailVerificationModel
from src.domain.entities.email_verification import EmailVerification
from src.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.infra.postgresql.connection import DBConnectionHandler
from src.infra.postgresql.mappers.email_verification_mapper import EmailVerificationMapper
from sqlalchemy import select, update

class UserEmailVerificationRepository(IUserEmailVerificationRepository):

    def __init__(self, db: DBConnectionHandler, user_email_verification_mapper: EmailVerificationMapper):
        self._db = db
        self._mapper = user_email_verification_mapper


    async def create_verification_code(self, email_verification: EmailVerification) -> EmailVerification:
        email_verification_model = self._mapper.to_model(email_verification)
        async with self._db.session() as session:
            session.add(email_verification_model)

            await session.refresh(email_verification_model)

            return self._mapper.to_entity(email_verification_model)


    async def get_by_code(self, hashed_code: str) -> Optional[EmailVerification]:
        async with self._db.session() as session:
            query = (
                select(UserEmailVerificationModel)
                .where(UserEmailVerificationModel.token_hash == hashed_code)

            )
            email_verification_model = await session.execute(query).scalar_one_or_none()

            if not email_verification_model:
                return None

            return self._mapper.to_entity(email_verification_model)

    async def revoke(self, email_verification: EmailVerification) -> None:
        email_verification_model = self._mapper.to_model(email_verification)
        async with self._db.session() as session:
            query = (
                 update(UserEmailVerificationModel)
                .where(UserEmailVerificationModel.id == email_verification_model.id)
                .values(revoked_at=email_verification_model.revoked_at)
            )

            await session.execute(query)

    async def validate_email_verification(self, email_verification: EmailVerification) -> None:
        email_verification_model = self._mapper.to_model(email_verification)
        async with self._db.session() as session:
            query = (
                 update(UserEmailVerificationModel)
                .where(UserEmailVerificationModel.id == email_verification_model.id)
                .values(verified_at=email_verification_model.verified_at)
            )

            await session.execute(query)


    async def get_active_email_verification_by_user_id(self, user_id: UserId) -> Optional[EmailVerification]:
        async with self._db.session() as session:
            query = (
                select(UserEmailVerificationModel)
                .where(UserEmailVerificationModel.user_id == str(user_id),
                       UserEmailVerificationModel.revoked_at.is_(None),
                       UserEmailVerificationModel.verified_at.is_(None))
            )
            email_verification_model = await session.execute(query).scalar_one_or_none()

            if not email_verification_model:
                return None

            return self._mapper.to_entity(email_verification_model)