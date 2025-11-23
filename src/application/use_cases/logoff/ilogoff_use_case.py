from abc import ABC, abstractmethod



class ILogoffUseCase(ABC):

    @abstractmethod
    async def execute(self, refresh_token: str) -> None:
        ...