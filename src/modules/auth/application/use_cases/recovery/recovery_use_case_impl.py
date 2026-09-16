from src.modules.auth.application.use_cases.recovery.irecovery_use_case import IRecoveryUseCase
from src.modules.auth.domain.events.user_account_recovered import UserAccountRecovered
from src.modules.auth.domain.exceptions.user_recovery_exceptions import UserRecoveryTokenError
from src.modules.auth.domain.exceptions.user_custom_exceptions import UserNotFoundError
from src.modules.auth.domain.ports.units_of_work.iauth_unit_of_work import IAuthUnitOfWork
from src.modules.internal_events.public import IOutboxService
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.ihasher_generator import IHasherGenerator


class RecoveryUseCaseImpl(IRecoveryUseCase):
    def __init__(
        self,
        auth_unit_of_work: IAuthUnitOfWork,
        hasher_generator: IHasherGenerator,
        system_clock: IClock,
        outbox_service: IOutboxService,
    ) -> None:
        self.__uow = auth_unit_of_work
        self.__hasher = hasher_generator
        self.__clock = system_clock
        self.__outbox_service = outbox_service

    async def execute(self, raw_code: str) -> None:
        if not raw_code or not raw_code.strip():
            raise UserRecoveryTokenError()

        hashed_code = self.__hasher.generate_hash(raw_code.strip())
        async with self.__uow as uow:
            recovery_request = (
                await uow.user_recovery_request_repository.find_by_hashed_token(
                    hashed_code
                )
            )
            if recovery_request is None:
                raise UserRecoveryTokenError()
            if recovery_request.is_confirmed or recovery_request.is_revoked:
                raise UserRecoveryTokenError()

            now = self.__clock.now()
            if recovery_request.is_expired(now):
                raise UserRecoveryTokenError()

            user = await uow.users_repository.find_deleted_by_id(
                recovery_request.user_id
            )
            if user is None:
                raise UserRecoveryTokenError()

            recovery_request.confirm(now)
            await uow.user_recovery_request_repository.mark_as_confirmed(
                recovery_request,
                now,
            )
            user.mark_as_recovered()
            try:
                await uow.users_repository.mark_as_recovered(user.id)
            except UserNotFoundError as exc:
                raise UserRecoveryTokenError() from exc
            await self.__outbox_service.persist_event(
                UserAccountRecovered(user_id=user.id, occurred_at=now),
                uow.outbox_repository,
            )
            await uow.commit()
