from abc import ABC, abstractmethod

from src.application.use_cases.refresh.dto import RefreshResultDTO


class IRefreshUseCase(ABC):

    @abstractmethod
    async def execute(self, refresh_token: str) -> RefreshResultDTO:
        ...