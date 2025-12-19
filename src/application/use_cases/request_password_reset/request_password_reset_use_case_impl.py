from irequest_password_reset_use_case import IRequestPasswordResetUseCase
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.ports.system.iclock import IClock
from src.domain.value_objects.email import Email


class RequestPasswordResetUseCaseImpl(IRequestPasswordResetUseCase):

    def __init__(self, user_repository: IUserRepository, password_reset_service, system_clock: IClock) -> None:
        self.__user_repository = user_repository
        self.__password_reset_service = password_reset_service
        self.__system_clock = system_clock


    async def execute(self, email: Email) -> None:
        user = await self.__user_repository.find_by_email(email)

        if not user:
            return  # Não revelar se o email existe ou não

        await self.__password_reset_service.issue_password_reset_for_user(user)