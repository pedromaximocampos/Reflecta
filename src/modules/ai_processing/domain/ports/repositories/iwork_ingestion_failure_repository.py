from typing import Protocol

from src.modules.ai_processing.domain.entities import WorkIngestionFailureAttempt


class IWorkIngestionFailureRepository(Protocol):
    async def create(
        self,
        failure: WorkIngestionFailureAttempt,
    ) -> WorkIngestionFailureAttempt: ...
