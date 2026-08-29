from typing import Protocol
from src.modules.auth.application.use_cases.refresh.dto import RefreshResultDTO


class IRefreshUseCase(Protocol):

    async def execute(self, refresh_token: str) -> RefreshResultDTO:
        ...