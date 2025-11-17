from src.application.use_cases.login import *
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.entities.user import User, AuthCredentials
from src.domain.ports.repositories.isession_repository import ISessionRepository
from src.domain.ports.security.itoken_service import ITokenService
from src.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.domain.ports.system.iclock import IClock
from src.domain.value_objects.password_hash import PasswordHash
from src.domain.exceptions.api_types import NotFoundError, AuthError


class LoginUseCaseImpl(ILoginUseCase):

    def __init__(self, user_repository: IUserRepository, session_repository: ISessionRepository, token_service: ITokenService,
                 password_hasher: IPasswordHasher, system_clock: IClock) -> None:
        self._user_repository = user_repository
        self._session_repository = session_repository
        self._token_service = token_service
        self._password_hasher = password_hasher
        self._system_clock = system_clock


    async def execute(self, login_input: LoginInput) -> LoginOutput:

        user: User = await self._get_credentials_by_email(login_input.email)

        password_hash:  PasswordHash = self._create_password_hash_v_o(user.auth_credentials)

        self._verify_password(login_input.password, password_hash)

        needs_rehash = self._password_hasher.needs_rehash(password_hash)

        now = self._system_clock.now()

        if needs_rehash:
            new_password_hash_v_o = self._password_hasher.hash(login_input.password)
            user.update_auth_credentials(new_password_hash_v_o, now)

        user.update_last_login(now)

        await self._user_repository.save(user)

        login_output: LoginOutput = self._create_login_output(user)

        return login_output


    @staticmethod
    def _create_password_hash_v_o(credentials: AuthCredentials) -> PasswordHash:
        return PasswordHash(
            algorithm=credentials.password_algorithm,
            hash=credentials.password_hash,
            version=credentials.password_version,
        )

    async def _get_credentials_by_email(self, email: str) -> User:
        user: User = await self._user_repository.find_by_email(email)
        if not user:
            raise NotFoundError("User not Found.")
        return user

    def _verify_password(self, plain_password: str, password_hash: PasswordHash) -> None:
        is_valid = self._password_hasher.verify(plain_password, password_hash)
        if not is_valid:
            raise AuthError("Credenciais inválidas.")


    def _create_login_output(self, user: User) -> LoginOutput:

        access_token = self._token_service.generate_token(user.id, self._system_clock.access_token_expiration())
        refresh_token = self._token_service.generate_token(user.id, self._system_clock.refresh_token_expiration())

        return LoginOutput(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            email=user.email,
            name=user.name,
            username=user.username,
            surname=user.surname,
        )
