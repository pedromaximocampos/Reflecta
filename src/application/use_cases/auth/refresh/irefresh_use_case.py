from typing import Protocol
from src.application.use_cases.auth.refresh.dto import RefreshResultDTO


class IRefreshUseCase(Protocol):

    async def execute(self, refresh_token: str) -> RefreshResultDTO:
        ...