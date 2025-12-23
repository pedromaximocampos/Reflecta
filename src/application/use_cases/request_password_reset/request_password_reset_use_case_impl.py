from irequest_password_reset_use_case import IRequestPasswordResetUseCase
from src.application.services.reset_password_service.ipassword_reset_service import IPasswordResetService
from src.domain.ports.repositories.iuser_repository import IUserRepository
from src.domain.ports.system.iclock import IClock
from src.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.domain.value_objects.email import Email


class RequestPasswordResetUseCaseImpl(IRequestPasswordResetUseCase):

    def __init__(self, auth_unit_of_work: IAuthUnitOfWork, password_reset_service: IPasswordResetService, system_clock: IClock) -> None:
        self.__auth_unit_of_work = auth_unit_of_work
        self.__password_reset_service = password_reset_service
        self.__system_clock = system_clock


    async def execute(self, email: Email) -> None:
        async with self.__auth_unit_of_work as uow:
            user = await uow.users_repository.find_by_email(email)

            if not user:
                return  # Não revelar se o email existe ou não

            await self.__password_reset_service.issue_for_user(user, uow)

            await uow.commit()