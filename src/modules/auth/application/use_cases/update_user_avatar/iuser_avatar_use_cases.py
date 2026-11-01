from typing import Protocol

from src.modules.auth.application.use_cases.update_user_info.dto import (
    UpdateUserInfoOutput,
)
from src.modules.auth.application.use_cases.update_user_avatar.dto import (
    RemoveUserAvatarInputDTO,
    ReplaceUserAvatarInputDTO,
)


class IReplaceUserAvatarUseCase(Protocol):
    async def execute(
        self,
        avatar_input: ReplaceUserAvatarInputDTO,
    ) -> UpdateUserInfoOutput: ...


class IRemoveUserAvatarUseCase(Protocol):
    async def execute(
        self,
        avatar_input: RemoveUserAvatarInputDTO,
    ) -> UpdateUserInfoOutput: ...
