from typing import Protocol

from src.modules.auth.domain.entities.user import User
from src.modules.auth.domain.events.emails.user_recovery_requested import UserRecoveryRequested
from src.modules.auth.domain.ports.repositories.iuser_recovery_request_repository import (
    IUserRecoveryRequestRepository,
)


class IUserRecoveryService(Protocol):
    async def issue_for_user(
        self,
        user: User,
        repository: IUserRecoveryRequestRepository,
    ) -> UserRecoveryRequested:
        ...
