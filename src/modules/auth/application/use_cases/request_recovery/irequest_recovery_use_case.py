from typing import Protocol


class IRequestRecoveryUseCase(Protocol):
    async def execute(self, email: str) -> None:
        ...
