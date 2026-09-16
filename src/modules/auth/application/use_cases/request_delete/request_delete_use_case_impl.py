from src.modules.auth.application.services.user_deletion.iuser_deletion_service import (
    IUserDeletionService,
)
from src.modules.auth.application.use_cases.request_delete.irequest_delete_use_case import (
    IRequestDeleteUseCase,
)
from src.modules.auth.domain.exceptions.user_custom_exceptions import UserNotFoundError
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.modules.auth.public.user_id import UserId
from src.modules.internal_events.public import IOutboxService


class RequestDeleteUseCaseImpl(IRequestDeleteUseCase):
    def __init__(
        self,
        auth_unit_of_work: IAuthUnitOfWork,
        user_deletion_service: IUserDeletionService,
        outbox_service: IOutboxService,
    ) -> None:
        self.__uow = auth_unit_of_work
        self.__user_deletion_service = user_deletion_service
        self.__outbox_service = outbox_service

    async def execute(self, user_id: UserId) -> None:
        async with self.__uow as uow:
            user = await uow.users_repository.find_by_id(user_id)
            if user is None:
                raise UserNotFoundError()

            event = await self.__user_deletion_service.issue_for_user(
                user,
                uow.user_deletion_request_repository,
            )
            await self.__outbox_service.persist_event(
                event,
                uow.outbox_repository,
            )
            await uow.commit()
