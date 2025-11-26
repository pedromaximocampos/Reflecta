from src.domain.entities.email_verification import EmailVerification
from src.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.infra.postgresql.connection import DBConnectionHandler
from src.infra.postgresql.mappers.email_verification_mapper import EmailVerificationMapper


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