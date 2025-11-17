from abc import ABC, abstractmethod

from src.application.use_cases.login import LoginInput, LoginOutput


class ILoginUseCase(ABC):

    @abstractmethod
    async def execute(self, login_input: LoginInput) -> LoginOutput:
        ...