from datetime import timedelta, datetime
import secrets
from isignup_use_case import ISignUpUseCase
from src.application.use_cases.signup.dto import SignupInputDTO, SignupOutputDTO
from src.domain.entities.email_verification import EmailVerification
from src.domain.entities.user import User, AuthCredentials
from src.domain.ports.repositories.iuser_email_verification_repository import IUserEmailVerificationRepository
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.domain.ports.system.iclock import IClock
from src.domain.ports.system.ihasher_generator import IHasherGenerator
from src.domain.ports.system.iulid_generator import IULIDGenerator
from src.domain.value_objects.password_hash import PasswordHash
from src.domain.value_objects.user_id import UserId
from src.domain.exceptions.custom_exceptions.user_custom_exceptions import UsernameAlreadyExistsError, EmailAlreadyExistsError

class SignupUseCaseImpl(ISignUpUseCase):

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        system_clock: IClock,
        ulid_generator: IULIDGenerator,
        hash_generator: IHasherGenerator,
        user_email_verification_repository: IUserEmailVerificationRepository
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._clock = system_clock
        self._ulid_generator = ulid_generator
        self._hash_generator = hash_generator
        self._email_verification_repo = user_email_verification_repository

    async def execute(self, dto: SignupInputDTO) -> SignupOutputDTO:

        now = self._clock.now()

        new_user = self._create_new_user_entity(dto, now)

        created_user = await self._user_repository.create(new_user)

        email_verif, raw_token = self._create_email_verification(created_user, now)
        # TODO: implement email verification creation

        await self._email_verification_repo.create_verification_code(email_verif)

        #TODO: Send verification email

        return SignupOutputDTO(
            user=created_user,
            raw_token_to_verify_email=raw_token
        )

    def _create_email_verification(self, user: User, now: datetime) -> tuple[EmailVerification, str]:
        raw = secrets.token_urlsafe(32)
        token_hash = self._hash_generator.generate_hash(raw)

        expires_at = now + timedelta(
            seconds=self._clock.email_verification_code_expiration_in_seconds()
        )

        verification = EmailVerification(
            id=self._ulid_generator.generate_ulid(),
            user_id=user.id,
            token_hash=token_hash,
            created_at=now,
            expires_at=expires_at
        )

        return verification, raw

    def _create_new_user_entity(self, dto: SignupInputDTO, now: datetime) -> User:
        user_id = UserId(self._ulid_generator.generate_ulid())

        password_hash = self._password_hasher.hash(dto.password)

        credentials = AuthCredentials(
            user_id=user_id,
            password=password_hash,
            created_at=now
        )

        return User(
            id=user_id,
            email=dto.email,
            name=dto.name,
            surname=dto.surname,
            date_of_birth=dto.date_of_birth,
            username=dto.username,
            created_at=now,
            auth_credentials=credentials,
            is_email_verified=False
        )
