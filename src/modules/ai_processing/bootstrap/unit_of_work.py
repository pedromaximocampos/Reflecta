from src.modules.ai_processing.domain.ports.unit_of_work import (
    IAIProcessingUnitOfWork,
)
from src.modules.ai_processing.infrastructure.persistence.postgresql.mappers import (
    InboxEventMapper,
    WorkIngestionChunkMapper,
)
from src.modules.ai_processing.infrastructure.persistence.postgresql.unit_of_work import (
    AIProcessingUnitOfWork,
)
from src.shared.infrastructure.persistence.postgresql.provider import (
    individuum_mvp_provider,
)


def get_ai_processing_unit_of_work() -> IAIProcessingUnitOfWork:
    return AIProcessingUnitOfWork(
        db=individuum_mvp_provider,
        work_ingestion_chunk_mapper=WorkIngestionChunkMapper(),
        inbox_event_mapper=InboxEventMapper(),
    )
