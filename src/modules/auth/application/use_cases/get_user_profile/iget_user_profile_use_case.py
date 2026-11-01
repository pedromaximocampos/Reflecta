from typing import Protocol

from src.modules.auth.application.use_cases.update_user_info.dto import (
    UpdateUserInfoOutput,
)
from src.modules.auth.public.user_id import UserId


class IGetUserProfileUseCase(Protocol):
    async def execute(self, user_id: UserId) -> UpdateUserInfoOutput: ...
