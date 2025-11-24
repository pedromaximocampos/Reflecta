from typing import Protocol


class ILogoffUseCase(Protocol):

    async def execute(self, refresh_token: str) -> None:
        ...