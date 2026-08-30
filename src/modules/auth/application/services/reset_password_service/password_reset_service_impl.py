import secrets
from datetime import timedelta, datetime

from .ipassword_reset_service import IPasswordResetService

from src.modules.auth.domain.entities.reset_password import ResetPassword
from src.modules.auth.domain.entities.user import User
from src.modules.auth.domain.events.emails.password_reset_requested import PasswordResetRequested
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.ihasher_generator import IHasherGenerator
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.modules.internal_events.public import IOutboxService


class PasswordResetServiceImpl(IPasswordResetService):


    def __init__(self, system_clock: IClock,
                 ulid_generator: IULIDGenerator, hasher_generator: IHasherGenerator,
                 ) -> None:
        self.__system_clock = system_clock
        self.__ulid_generator = ulid_generator
        self.__hashing_generator = hasher_generator

    def __create_reset_password_entity(self, user: User, now: datetime) -> tuple[ResetPassword, str]:
        raw_code  = secrets.token_urlsafe(32)
        code_hash = self.__hashing_generator.generate_hash(raw_code)

        new_id  = self.__ulid_generator.generate_ulid()
        expires_at = now + timedelta(seconds=self.__system_clock.password_reset_expiration_in_seconds())

        reset_password_entity = ResetPassword(new_id, user.id, code_hash, now, expires_at)

        return reset_password_entity, raw_code

    @staticmethod
    def __create_password_reset_event(user: User, raw_code: str, now: datetime) -> PasswordResetRequested:
        password_reset_event = PasswordResetRequested(user.id, user.username, user.email, raw_code, now)
        return password_reset_event


    async def issue_for_user(self, user: User, uow: IAuthUnitOfWork) -> PasswordResetRequested:
        now = self.__system_clock.now()
        reset_password_entity, raw_code = self.__create_reset_password_entity(user, now)

        created_reset_password_entity = await uow.reset_password_repository.create_new_password_reset(reset_password_entity)

        password_reset_event = self.__create_password_reset_event(user, raw_code, now)


        return password_reset_event
