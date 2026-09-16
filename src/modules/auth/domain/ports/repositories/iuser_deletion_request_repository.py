from datetime import datetime
from typing import Optional, Protocol

from src.modules.auth.domain.entities.user_deletion_request import UserDeletionRequest
from src.modules.auth.public.user_id import UserId


class IUserDeletionRequestRepository(Protocol):
    async def create(
        self,
        deletion_request: UserDeletionRequest,
    ) -> UserDeletionRequest:
        ...

    async def find_by_hashed_token(
        self,
        hashed_token: str,
    ) -> Optional[UserDeletionRequest]:
        ...

    async def get_active_by_user_id(
        self,
        user_id: UserId,
    ) -> Optional[UserDeletionRequest]:
        ...

    async def revoke(self, deletion_request: UserDeletionRequest) -> None:
        ...

    async def mark_as_confirmed(
        self,
        deletion_request: UserDeletionRequest,
        confirmed_at: datetime,
    ) -> None:
        ...
