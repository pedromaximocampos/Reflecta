import secrets
from datetime import timedelta

from src.modules.auth.application.services.user_deletion.iuser_deletion_service import (
    IUserDeletionService,
)
from src.modules.auth.domain.entities.user import User
from src.modules.auth.domain.entities.user_deletion_request import UserDeletionRequest
from src.modules.auth.domain.events.emails.user_deletion_requested import UserDeletionRequested
from src.modules.auth.domain.ports.repositories.iuser_deletion_request_repository import (
    IUserDeletionRequestRepository,
)
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.ihasher_generator import IHasherGenerator
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


class UserDeletionServiceImpl(IUserDeletionService):
    def __init__(
        self,
        system_clock: IClock,
        ulid_generator: IULIDGenerator,
        hasher_generator: IHasherGenerator,
    ) -> None:
        self.__clock = system_clock
        self.__ulid_generator = ulid_generator
        self.__hasher = hasher_generator

    async def issue_for_user(
        self,
        user: User,
        repository: IUserDeletionRequestRepository,
    ) -> UserDeletionRequested:
        now = self.__clock.now()
        active_request = await repository.get_active_by_user_id(user.id)
        if active_request is not None:
            active_request.revoke(now)
            await repository.revoke(active_request)

        raw_code = secrets.token_urlsafe(32)
        expires_at = now + timedelta(
            seconds=self.__clock.user_deletion_expiration_in_seconds()
        )
        deletion_request = UserDeletionRequest(
            id=self.__ulid_generator.generate_ulid(),
            user_id=user.id,
            token_hash=self.__hasher.generate_hash(raw_code),
            created_at=now,
            expires_at=expires_at,
        )
        await repository.create(deletion_request)

        return UserDeletionRequested(
            user_id=user.id,
            username=user.username,
            user_email=user.email,
            raw_code=raw_code,
            expires_in_minutes=int((expires_at - now).total_seconds() // 60),
            occurred_at=now,
        )
