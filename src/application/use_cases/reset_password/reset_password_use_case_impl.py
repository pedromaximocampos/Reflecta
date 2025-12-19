from ireset_password_use_case import IResetPasswordUseCase
from src.application.services.reset_password_service.ipassword_reset_service import IPasswordResetService
from src.domain.entities.reset_password import ResetPassword
from src.domain.entities.user import User
from src.domain.exceptions.custom_exceptions.passwords_exceptions import ResetPasswordTokenException
from src.domain.ports.repositories.ireset_password_repository import IResetPasswordRepository
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.domain.ports.system.iclock import IClock
from src.domain.ports.system.ihasher_generator import IHasherGenerator
from src.domain.value_objects.password_plain import PasswordPlain
from src.domain.value_objects.user_id import UserId


class ResetPasswordUseCase(IResetPasswordUseCase):

    def __init__(self, user_repository: IUserRepository, system_clock: IClock, reset_password_repository: IResetPasswordRepository,
                 hasher_generator: IHasherGenerator, password_hasher: IPasswordHasher) -> None:
        self.__user_repository = user_repository
        self.__system_clock = system_clock
        self.__reset_password_repository = reset_password_repository
        self.__hasher_generator = hasher_generator
        self.__password_hasher = password_hasher


    async def __validate_reset_token(self, reset_raw_token: str) -> ResetPassword:
        hashed_reset_token = self.__hasher_generator.generate_hash(reset_raw_token)

        reset_password_entity  = await self.__reset_password_repository.find_by_hashed_token(hashed_reset_token)

        if not reset_password_entity:
            raise ResetPasswordTokenException("Invalid token.")

        return reset_password_entity

    async def __validate_user(self, user_id: UserId) -> User:
        user = await self.__user_repository.find_by_id(user_id)

        if not user:
            raise ResetPasswordTokenException("User not found.")

        return user

    async def execute(self, reset_raw_token: str, new_password: str) -> None:
        now = self.__system_clock.now()

        reset_password_entity = await self.__validate_reset_token(reset_raw_token)

        if reset_password_entity.is_used:
            raise ResetPasswordTokenException("Token has already been used.")

        if reset_password_entity.is_expired:
            raise ResetPasswordTokenException("Token has expired.")

        user = await self.__validate_user(reset_password_entity.user_id)

        password_plain = PasswordPlain(new_password)

        hashed_new_password = password_plain.to_hash(self.__password_hasher)

        user.update_auth_credentials(hashed_new_password, now)

        await self.__user_repository.update_auth_credentials(user)





