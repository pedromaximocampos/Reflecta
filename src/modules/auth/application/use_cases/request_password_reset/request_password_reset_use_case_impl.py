from src.modules.internal_events.public import IOutboxService
from .irequest_password_reset_use_case import IRequestPasswordResetUseCase
from src.modules.auth.application.services.reset_password_service.ipassword_reset_service import IPasswordResetService
from src.domain.ports.system.iclock import IClock
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.modules.auth.public.email import Email


class RequestPasswordResetUseCaseImpl(IRequestPasswordResetUseCase):

    def __init__(self, auth_unit_of_work: IAuthUnitOfWork, password_reset_service: IPasswordResetService, system_clock: IClock,
                 outbox_service: IOutboxService) -> None:
        self.__auth_unit_of_work = auth_unit_of_work
        self.__password_reset_service = password_reset_service
        self.__system_clock = system_clock
        self.__outbox_service = outbox_service


    async def execute(self, email: str) -> None:
        async with self.__auth_unit_of_work as uow:
            email_input = Email(email)
            user = await uow.users_repository.find_by_email(email_input)

            if not user:
                return  # Não revelar se o email existe ou não

            password_reset_event = await self.__password_reset_service.issue_for_user(user, uow.reset_password_repository)

            await self.__outbox_service.persist_event(password_reset_event, uow.outbox_repository)

            await uow.commit()