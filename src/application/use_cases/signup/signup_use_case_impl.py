from datetime import datetime
from isignup_use_case import ISignUpUseCase
from src.application.services.email_verification.iemail_verification_service import IEmailVerificationService
from src.application.use_cases.signup.dto import SignupInputDTO, SignupOutputDTO
from src.domain.entities.user import User, AuthCredentials
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.domain.ports.system.iclock import IClock
from src.domain.ports.system.ihasher_generator import IHasherGenerator
from src.domain.ports.system.iulid_generator import IULIDGenerator
from src.domain.value_objects.user_id import UserId


class SignupUseCaseImpl(ISignUpUseCase):

    def __init__(
        self,
        user_repository: IUserRepository,
        password_hasher: IPasswordHasher,
        system_clock: IClock,
        ulid_generator: IULIDGenerator,
        hash_generator: IHasherGenerator,
        email_verification_service: IEmailVerificationService,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._clock = system_clock
        self._ulid_generator = ulid_generator
        self._hash_generator = hash_generator
        self._email_verification_service = email_verification_service

    async def execute(self, dto: SignupInputDTO) -> SignupOutputDTO:

        created_user = await self._create_new_user_(dto)

        email_verification, raw_token = await self._email_verification_service.issue_for_user(created_user)

        return SignupOutputDTO(
            user=created_user,
            raw_token_to_verify_email=raw_token
        )


    async def _create_new_user_(self, dto: SignupInputDTO) -> User:
        now = self._clock.now()

        user_id = UserId(self._ulid_generator.generate_ulid())

        password_hash = self._password_hasher.hash(dto.password)

        credentials = AuthCredentials(
            user_id=user_id,
            password=password_hash,
            created_at=now
        )

        new_user = User(
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

        created_user = await self._user_repository.create(new_user)

        return created_user
