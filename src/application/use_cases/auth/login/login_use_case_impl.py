from src.application.services.auth.email_verification.iemail_verification_service import IEmailVerificationService
from src.application.services.messaging.ioutbox_service import IOutboxService
from src.application.use_cases.auth.login import *
from src.domain.entities.user import User, AuthCredentials
from src.domain.exceptions.custom_exceptions.email_verification_exceptions import EmailVerificationException
from src.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.domain.ports.system.iclock import IClock
from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.domain.value_objects.email import Email
from src.domain.value_objects.password_hash import PasswordHash
from src.domain.exceptions.api_types import AuthError
from src.application.services.auth.auth_session import *


class LoginUseCaseImpl(ILoginUseCase):

    def __init__(self,password_hasher: IPasswordHasher, system_clock: IClock,
                 auth_session_service: IAuthSessionService, email_verification_service: IEmailVerificationService,
                 auth_unit_of_work: IAuthUnitOfWork, outbox_service: IOutboxService) -> None:
        self.__password_hasher = password_hasher
        self.__system_clock = system_clock
        self.__auth_session_service = auth_session_service
        self.__email_verification_service = email_verification_service
        self.__auth_unit_of_work = auth_unit_of_work
        self.__outbox_service = outbox_service


    async def execute(self, login_input: LoginInput) -> LoginOutput:

        async with self.__auth_unit_of_work as uow:

            user: User = await self.__get_credentials_by_email(login_input.email, uow)

            password_hash:  PasswordHash = self.__create_password_hash_v_o(user.auth_credentials)

            self.__verify_password(login_input.password, password_hash)

            await self.__verify_user_email_is_verified(user, uow)

            needs_rehash = self.__password_hasher.needs_rehash(password_hash)

            now = self.__system_clock.now()

            if needs_rehash:
                new_password_hash_v_o = self.__password_hasher.hash(login_input.password)
                user.update_auth_credentials(new_password_hash_v_o, now)

                await uow.users_repository.update_auth_credentials(user)

            user.update_last_login(now)

            await uow.users_repository.update_last_login_at(user)

            auth_session_result: AuthSessionResultDTO = await self.__auth_session_service.create_session(user, uow)

            login_output: LoginOutput = self.__create_login_output(user, auth_session_result)

            await uow.commit()

            return login_output


    async def __verify_user_email_is_verified(self, user: User, uow: IAuthUnitOfWork) -> None:
        if not user.is_email_verified:
            event = await self.__email_verification_service.ensure_or_issue(user, uow.user_email_verification_repository)

            if event is not None:
                await self.__outbox_service.persist_event(event, uow.outbox_repository)
                raise EmailVerificationException()

            raise EmailVerificationException("Existing verification is still active. Please verify your email.")

    @staticmethod
    def __create_password_hash_v_o(credentials: AuthCredentials) -> PasswordHash:
        return PasswordHash(
            algorithm=credentials.password.algorithm,
            hash=credentials.password.hash,
            version=credentials.password.version,
        )

    @staticmethod
    async def __get_credentials_by_email(email: Email, uow: IAuthUnitOfWork) -> User:
        user: User = await uow.users_repository.find_by_email(email)
        if not user:
            raise AuthError("Invalid username or password")
        return user

    def __verify_password(self, plain_password: str, password_hash: PasswordHash) -> None:
        is_valid = self.__password_hasher.verify(plain_password, password_hash)
        if not is_valid:
            raise AuthError("Invalid username or password")

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
