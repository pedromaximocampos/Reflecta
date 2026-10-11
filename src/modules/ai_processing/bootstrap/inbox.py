from src.modules.ai_processing.application.ports.inbox import IWorkIngestionInbox
from src.modules.ai_processing.application.services import WorkIngestionInboxService
from src.modules.ai_processing.bootstrap.unit_of_work import (
    get_ai_processing_unit_of_work,
)
from src.shared.infrastructure.system.providers import get_clock


WORK_INGESTION_CONSUMER_NAME = "ai_processing.work_ingestion.v1"


def get_work_ingestion_inbox() -> IWorkIngestionInbox:
    return WorkIngestionInboxService(
        uow=get_ai_processing_unit_of_work(),
        clock=get_clock(),
        consumer_name=WORK_INGESTION_CONSUMER_NAME,
    )
