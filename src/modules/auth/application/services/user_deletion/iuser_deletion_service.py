from typing import Protocol

from src.modules.auth.domain.entities.user import User
from src.modules.auth.domain.events.emails.user_deletion_requested import UserDeletionRequested
from src.modules.auth.domain.ports.repositories.iuser_deletion_request_repository import (
    IUserDeletionRequestRepository,
)


class IUserDeletionService(Protocol):
    async def issue_for_user(
        self,
        user: User,
        repository: IUserDeletionRequestRepository,
    ) -> UserDeletionRequested:
        ...
