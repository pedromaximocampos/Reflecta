from datetime import datetime
from typing import Optional, Protocol

from src.modules.auth.domain.entities.user_recovery_request import UserRecoveryRequest
from src.modules.auth.public.user_id import UserId


class IUserRecoveryRequestRepository(Protocol):
    async def create(
        self,
        recovery_request: UserRecoveryRequest,
    ) -> UserRecoveryRequest:
        ...

    async def find_by_hashed_token(
        self,
        hashed_token: str,
    ) -> Optional[UserRecoveryRequest]:
        ...

    async def get_active_by_user_id(
        self,
        user_id: UserId,
    ) -> Optional[UserRecoveryRequest]:
        ...

    async def revoke(self, recovery_request: UserRecoveryRequest) -> None:
        ...

    async def mark_as_confirmed(
        self,
        recovery_request: UserRecoveryRequest,
        confirmed_at: datetime,
    ) -> None:
        ...
