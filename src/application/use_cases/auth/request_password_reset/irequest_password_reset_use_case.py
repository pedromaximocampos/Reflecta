from typing import Protocol

from src.domain.value_objects.email import Email


class IRequestPasswordResetUseCase(Protocol):

    async def execute(self, email: Email) -> None:
        ...