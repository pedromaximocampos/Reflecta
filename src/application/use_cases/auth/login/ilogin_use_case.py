from typing import Protocol
from src.application.use_cases.auth.login import LoginInput, LoginOutput


class ILoginUseCase(Protocol):

    async def execute(self, login_input: LoginInput) -> LoginOutput: ...