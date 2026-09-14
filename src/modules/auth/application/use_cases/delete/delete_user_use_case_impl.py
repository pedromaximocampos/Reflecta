from src.modules.auth.application.services.auth_session.iauth_session_service import (
    IAuthSessionService,
)
from src.modules.auth.application.use_cases.delete.idelete_user_use_case import (
    IDeleteUserUseCase,
)
from src.modules.auth.domain.events.user_account_deleted import UserAccountDeleted
from src.modules.auth.domain.exceptions.user_deletion_exceptions import UserDeletionTokenError
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.modules.internal_events.public import IOutboxService
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.ihasher_generator import IHasherGenerator


class DeleteUserUseCaseImpl(IDeleteUserUseCase):
    def __init__(
        self,
        auth_unit_of_work: IAuthUnitOfWork,
        hasher_generator: IHasherGenerator,
        system_clock: IClock,
        auth_session_service: IAuthSessionService,
        outbox_service: IOutboxService,
    ) -> None:
        self.__uow = auth_unit_of_work
        self.__hasher = hasher_generator
        self.__clock = system_clock
        self.__auth_session_service = auth_session_service
        self.__outbox_service = outbox_service

    async def execute(self, raw_code: str) -> None:
        if not raw_code or not raw_code.strip():
            raise UserDeletionTokenError()

        hashed_code = self.__hasher.generate_hash(raw_code.strip())
        async with self.__uow as uow:
            deletion_request = (
                await uow.user_deletion_request_repository.find_by_hashed_token(
                    hashed_code
                )
            )
            if deletion_request is None:
                raise UserDeletionTokenError()
            if deletion_request.is_confirmed or deletion_request.is_revoked:
                raise UserDeletionTokenError()

            now = self.__clock.now()
            if deletion_request.is_expired(now):
                raise UserDeletionTokenError()

            user = await uow.users_repository.find_by_id(deletion_request.user_id)
            if user is None:
                raise UserDeletionTokenError()

            deletion_request.confirm(now)
            await uow.user_deletion_request_repository.mark_as_confirmed(
                deletion_request,
                now,
            )

            user.mark_as_deleted(now)
            await uow.users_repository.mark_as_deleted(user.id, now)
            await self.__auth_session_service.invalidate_all_sessions_for_user(
                user.id,
                uow,
            )
            await self.__outbox_service.persist_event(
                UserAccountDeleted(user_id=user.id, occurred_at=now),
                uow.outbox_repository,
            )
            await uow.commit()
