from ireset_password_use_case import IResetPasswordUseCase
from src.application.services.auth_session import IAuthSessionService
from src.application.services.reset_password_service.ipassword_reset_service import IPasswordResetService
from src.domain.entities.reset_password import ResetPassword
from src.domain.entities.user import User
from src.domain.exceptions.custom_exceptions.passwords_exceptions import ResetPasswordTokenException
from src.domain.ports.repositories.ireset_password_repository import IResetPasswordRepository
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.domain.ports.system.iclock import IClock
from src.domain.ports.system.ihasher_generator import IHasherGenerator
from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.domain.value_objects.password_plain import PasswordPlain
from src.domain.value_objects.user_id import UserId


class ResetPasswordUseCaseImpl(IResetPasswordUseCase):

    def __init__(self, system_clock: IClock, auth_unit_of_work: IAuthUnitOfWork,
                 hasher_generator: IHasherGenerator, password_hasher: IPasswordHasher, auth_sessions_service: IAuthSessionService) -> None:
        self.__auth_unit_of_work = auth_unit_of_work
        self.__system_clock = system_clock
        self.__hasher_generator = hasher_generator
        self.__password_hasher = password_hasher
        self.__auth_sessions_service = auth_sessions_service

    async def __validate_reset_token(self, reset_raw_token: str, uow: IAuthUnitOfWork) -> ResetPassword:
        hashed_reset_token = self.__hasher_generator.generate_hash(reset_raw_token)

        reset_password_entity  = await uow.reset_password_repository.find_by_hashed_token(hashed_reset_token)

        if not reset_password_entity:
            raise ResetPasswordTokenException("Invalid token.")

        if reset_password_entity.is_used:
            raise ResetPasswordTokenException("Token has already been used.")

        if reset_password_entity.is_expired:
            raise ResetPasswordTokenException("Token has expired.")

        return reset_password_entity

    @staticmethod
    async def __validate_user(user_id: UserId, uow: IAuthUnitOfWork) -> User:
        user = await uow.users_repository.find_by_id(user_id)

        if not user:
            raise ResetPasswordTokenException("User not found.")

        return user

    async def execute(self, reset_raw_token: str, new_password: str) -> None:
        now = self.__system_clock.now()

        async with self.__auth_unit_of_work as uow:
            reset_password_entity = await self.__validate_reset_token(reset_raw_token, uow)

            user = await self.__validate_user(reset_password_entity.user_id, uow)

            password_plain = PasswordPlain(new_password)

            hashed_new_password = password_plain.to_hash(self.__password_hasher)

            user.update_auth_credentials(hashed_new_password, now)

            await uow.users_repository.update_auth_credentials(user)

            reset_password_entity.mark_as_used(now)

            await uow.reset_password_repository.update_as_used(reset_password_entity)

            await self.__auth_sessions_service.invalidate_all_sessions_for_user(user.id, uow)

            await uow.commit()
