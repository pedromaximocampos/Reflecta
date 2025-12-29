from typing import Protocol


class IResetPasswordUseCase(Protocol):

    async def execute(self, reset_raw_token: str, new_password: str) -> None:
        ...