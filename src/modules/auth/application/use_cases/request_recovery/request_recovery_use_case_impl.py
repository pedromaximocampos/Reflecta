from src.modules.auth.application.services.user_recovery.iuser_recovery_service import (
    IUserRecoveryService,
)
from src.modules.auth.application.use_cases.request_recovery.irequest_recovery_use_case import (
    IRequestRecoveryUseCase,
)
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.modules.auth.public.email import Email
from src.modules.internal_events.public import IOutboxService


class RequestRecoveryUseCaseImpl(IRequestRecoveryUseCase):
    def __init__(
        self,
        auth_unit_of_work: IAuthUnitOfWork,
        user_recovery_service: IUserRecoveryService,
        outbox_service: IOutboxService,
    ) -> None:
        self.__uow = auth_unit_of_work
        self.__user_recovery_service = user_recovery_service
        self.__outbox_service = outbox_service

    async def execute(self, email: str) -> None:
        email_input = Email(email)
        async with self.__uow as uow:
            user = await uow.users_repository.find_deleted_by_email(email_input)
            if user is None:
                return

            event = await self.__user_recovery_service.issue_for_user(
                user,
                uow.user_recovery_request_repository,
            )
            await self.__outbox_service.persist_event(event, uow.outbox_repository)
            await uow.commit()
