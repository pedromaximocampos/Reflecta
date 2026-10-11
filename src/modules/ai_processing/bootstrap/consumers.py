from src.modules.ai_processing.application.use_cases.process_work_ingestion import (
    IProcessWorkIngestionUseCase,
)
from src.modules.ai_processing.bootstrap.inbox import get_work_ingestion_inbox
from src.modules.ai_processing.infrastructure.messaging.aws_sqs import (
    SQSWorkIngestionConsumerWorker,
)
from src.modules.ai_processing.infrastructure.messaging.aws_sqs.clients import (
    make_sqs_client,
)
from src.modules.ai_processing.infrastructure.messaging.aws_sqs.configs import (
    WorkIngestionSQSSettings,
)
from src.shared.config.settings import get_settings


def build_work_ingestion_consumer(
    use_case: IProcessWorkIngestionUseCase,
) -> SQSWorkIngestionConsumerWorker:
    settings = get_settings()
    sqs_settings = WorkIngestionSQSSettings(
        aws_region=settings.AWS_SQS_REGION,
        queue_url=settings.AWS_SQS_WORK_INGESTIONS_QUEUE_URL,
        aws_profile=settings.AWS_PROFILE,
        wait_time_seconds=settings.AI_WORK_INGESTION_WAIT_TIME_SECONDS,
        visibility_timeout_seconds=(
            settings.AI_WORK_INGESTION_VISIBILITY_TIMEOUT_SECONDS
        ),
        heartbeat_interval_seconds=(
            settings.AI_WORK_INGESTION_HEARTBEAT_INTERVAL_SECONDS
        ),
    )
    return SQSWorkIngestionConsumerWorker(
        client=make_sqs_client(sqs_settings),
        settings=sqs_settings,
        use_case=use_case,
        inbox=get_work_ingestion_inbox(),
    )
