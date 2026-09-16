from typing import Protocol

from src.modules.auth.application.use_cases.update_user_info.dto import (
    UpdateUserInfoInput,
    UpdateUserInfoOutput,
)


class IUpdateUserInfoUseCase(Protocol):
    async def execute(self, dto: UpdateUserInfoInput) -> UpdateUserInfoOutput:
        ...
