from datetime import datetime
from typing import Protocol

from src.modules.sharing.domain.entities import ProfessionalActivity, ShareAccess
from src.modules.sharing.domain.value_objects import ActivityStatus


class IProfessionalActivityRepository(Protocol):
    async def find_active_access_for_update(
        self,
        token: str,
        now: datetime,
    ) -> ShareAccess | None: ...

    async def count_for_share(self, share_id: str) -> int: ...

    async def add_many(
        self,
        activities: tuple[ProfessionalActivity, ...],
    ) -> tuple[ProfessionalActivity, ...]: ...

    async def list_for_user(
        self,
        user_id: str,
        status: ActivityStatus | None,
        limit: int,
        offset: int,
    ) -> tuple[ProfessionalActivity, ...]: ...

    async def count_for_user(
        self,
        user_id: str,
        status: ActivityStatus | None,
    ) -> int: ...

    async def find_for_user_for_update(
        self,
        activity_id: str,
        user_id: str,
    ) -> ProfessionalActivity | None: ...

    async def save(
        self,
        activity: ProfessionalActivity,
    ) -> ProfessionalActivity: ...

