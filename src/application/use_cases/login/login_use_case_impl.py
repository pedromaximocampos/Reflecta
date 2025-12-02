from src.application.services.email_verification.iemail_verification_service import IEmailVerificationService
from src.application.use_cases.login import *
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.entities.user import User, AuthCredentials
from src.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.domain.ports.system.iclock import IClock
from src.domain.value_objects.email import Email
from src.domain.value_objects.password_hash import PasswordHash
from src.domain.exceptions.api_types import NotFoundError, AuthError
from src.application.services.auth_session import *


class LoginUseCaseImpl(ILoginUseCase):

    def __init__(self, user_repository: IUserRepository, password_hasher: IPasswordHasher, system_clock: IClock,
                 auth_session_service: IAuthSessionService, email_verification_service: IEmailVerificationService) -> None:
        self.__user_repository = user_repository
        self.__password_hasher = password_hasher
        self.__system_clock = system_clock
        self.__auth_session_service = auth_session_service
        self.__email_verification_service = email_verification_service


    async def execute(self, login_input: LoginInput) -> LoginOutput:

        user: User = await self.__get_credentials_by_email(login_input.email)

        password_hash:  PasswordHash = self.__create_password_hash_v_o(user.auth_credentials)

        self.__verify_password(login_input.password, password_hash)

        if not user.is_email_verified:
            await self.__email_verification_service.ensure_active_verification_for_user(user)

        needs_rehash = self.__password_hasher.needs_rehash(password_hash)

        now = self.__system_clock.now()

        if needs_rehash:
            new_password_hash_v_o = self.__password_hasher.hash(login_input.password)
            user.update_auth_credentials(new_password_hash_v_o, now)

            await self.__user_repository.update_auth_credentials(user)

        user.update_last_login(now)

        await self.__user_repository.update_last_login_at(user)

        auth_session_result: AuthSessionResultDTO = await self.__auth_session_service.create_session(user)

        login_output: LoginOutput = self.__create_login_output(user, auth_session_result)

        return login_output


    @staticmethod
    def __create_password_hash_v_o(credentials: AuthCredentials) -> PasswordHash:
        return PasswordHash(
            algorithm=credentials.password.algorithm,
            hash=credentials.password.hash,
            version=credentials.password.version,
        )

    async def __get_credentials_by_email(self, email: Email) -> User:
        user: User = await self.__user_repository.find_by_email(email)
        if not user:
            raise NotFoundError("User not Found.")
        return user

    def __verify_password(self, plain_password: str, password_hash: PasswordHash) -> None:
        is_valid = self.__password_hasher.verify(plain_password, password_hash)
        if not is_valid:
            raise AuthError("Credenciais inválidas.")

    @staticmethod
    def __create_login_output(user: User, auth_session_result: AuthSessionResultDTO) -> LoginOutput:

        return LoginOutput(
            access_token=auth_session_result.access_token,
            refresh_token=auth_session_result.refresh_token,
            user_id=user.id,
            email=user.email,
            name=user.name,
            username=user.username,
            surname=user.surname,
            avatar_url=user.avatar_url,
        )
