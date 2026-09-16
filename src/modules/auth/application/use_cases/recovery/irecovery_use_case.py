from typing import Protocol


class IRecoveryUseCase(Protocol):
    async def execute(self, raw_code: str) -> None:
        ...
