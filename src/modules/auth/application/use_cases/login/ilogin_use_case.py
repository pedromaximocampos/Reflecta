from typing import Protocol

from .dto import LoginInput, LoginOutput


class ILoginUseCase(Protocol):

    async def execute(self, login_input: LoginInput) -> LoginOutput: ...
