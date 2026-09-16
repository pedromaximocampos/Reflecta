from typing import Protocol

from src.modules.auth.public.user_id import UserId


class IRequestDeleteUseCase(Protocol):
    async def execute(self, user_id: UserId) -> None:
        ...
