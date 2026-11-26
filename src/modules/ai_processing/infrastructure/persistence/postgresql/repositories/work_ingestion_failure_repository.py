from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.ai_processing.domain.entities import WorkIngestionFailureAttempt
from src.modules.ai_processing.domain.ports.repositories import (
    IWorkIngestionFailureRepository,
)
from src.modules.ai_processing.infrastructure.persistence.postgresql.models import (
    WorkIngestionFailureAttemptModel,
)


class WorkIngestionFailureRepository(IWorkIngestionFailureRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        failure: WorkIngestionFailureAttempt,
    ) -> WorkIngestionFailureAttempt:
        self._session.add(
            WorkIngestionFailureAttemptModel(
                id=failure.id,
                ingestion_id=failure.ingestion_id.value,
                chunk_id=failure.chunk_id.value if failure.chunk_id else None,
                stage=failure.stage,
                attempt=failure.attempt,
                error_code=failure.error_code,
                error_message=failure.error_message,
                occurred_at=failure.occurred_at,
                start_page=failure.start_page,
                end_page=failure.end_page,
                start_offset=failure.start_offset,
                end_offset=failure.end_offset,
                content_sha256=failure.content_sha256,
                provider_request_id=failure.provider_request_id,
                provider_response_id=failure.provider_response_id,
                context_text=failure.context_text,
            )
        )
        await self._session.flush()
        return failure
