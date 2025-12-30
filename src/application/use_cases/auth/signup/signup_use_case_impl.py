from src.domain.exceptions.custom_exceptions.user_custom_exceptions import EmailAlreadyExistsError
from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.domain.value_objects.email import Email
from src.domain.value_objects.password_plain import PasswordPlain
from .isignup_use_case import ISignUpUseCase
from src.application.services.email_verification.iemail_verification_service import IEmailVerificationService
from src.application.use_cases.auth.signup.dto import SignupInputDTO, SignupOutputDTO
from src.domain.entities.user import User, AuthCredentials
from src.domain.ports.security.ipassword_hasher import IPasswordHasher
from src.domain.ports.system.iclock import IClock
from src.domain.ports.system.ihasher_generator import IHasherGenerator
from src.domain.ports.system.iulid_generator import IULIDGenerator
from src.domain.value_objects.user_id import UserId


class SignupUseCaseImpl(ISignUpUseCase):

    def __init__(
        self,
        auth_unit_of_work: IAuthUnitOfWork,
        password_hasher: IPasswordHasher,
        system_clock: IClock,
        ulid_generator: IULIDGenerator,
        hash_generator: IHasherGenerator,
        email_verification_service: IEmailVerificationService,
    ) -> None:
        self.__auth_unit_of_work = auth_unit_of_work
        self.__password_hasher = password_hasher
        self.__clock = system_clock
        self.__ulid_generator = ulid_generator
        self.__hash_generator = hash_generator
        self.__email_verification_service = email_verification_service

    async def execute(self, dto: SignupInputDTO) -> SignupOutputDTO:

        async with self.__auth_unit_of_work as uow:


            created_user = await self.__create_new_user_(dto, uow)

            email_verification, raw_token = await self.__email_verification_service.issue_for_user(created_user, uow)

            await uow.commit()

            return SignupOutputDTO(
                user=created_user,
                raw_token_to_verify_email=raw_token
            )

    @staticmethod
    async def __check_email_already_exists_(email: Email, uow: IAuthUnitOfWork) -> bool:
        existing_user = await uow.users_repository.find_by_email(email)
        return existing_user is not None

    async def __create_new_user_(self, dto: SignupInputDTO, uow: IAuthUnitOfWork) -> User:

        user_email = Email(dto.email)

        existent_user = self.__check_email_already_exists_(user_email, uow)

        if existent_user:
            raise EmailAlreadyExistsError()

        now = self.__clock.now()

        user_id = UserId(self.__ulid_generator.generate_ulid())

        password_plain  = PasswordPlain(dto.password)

        password_hash = password_plain.to_hash(self.__password_hasher)

        credentials = AuthCredentials(
            user_id=user_id,
            password=password_hash,
            created_at=now
        )

        new_user = User(
            id=user_id,
            email=user_email,
            name=dto.name,
            surname=dto.surname,
            date_of_birth=dto.date_of_birth,
            username=dto.username,
            created_at=now,
            auth_credentials=credentials,
            is_email_verified=False
        )

        created_user = await uow.users_repository.create(new_user)

        return created_user
