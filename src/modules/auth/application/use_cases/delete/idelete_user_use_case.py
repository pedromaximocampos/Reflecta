from typing import Protocol


class IDeleteUserUseCase(Protocol):
    async def execute(self, raw_code: str) -> None:
        ...
