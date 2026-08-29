from typing import Protocol

from src.modules.auth.public.email import Email


class IRequestPasswordResetUseCase(Protocol):

    async def execute(self, email: str) -> None:
        ...