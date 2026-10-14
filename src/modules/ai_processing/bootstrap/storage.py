from src.modules.ai_processing.application.ports.storage import IWorkIngestionStorage
from src.modules.ai_processing.infrastructure.storage.aws.s3 import (
    S3WorkIngestionStorage,
)
from src.modules.ai_processing.infrastructure.storage.aws.s3.clients import (
    make_s3_client,
)
from src.modules.ai_processing.infrastructure.storage.aws.s3.configs import S3Settings
from src.shared.config.settings import get_settings


def get_work_ingestion_storage() -> IWorkIngestionStorage:
    settings = get_settings()
    storage_settings = S3Settings(
        aws_region=settings.AWS_S3_REGION,
        bucket_name=settings.AWS_S3_WORKS_BUCKET,
        aws_profile=settings.AWS_PROFILE,
    )
    return S3WorkIngestionStorage(
        client=make_s3_client(storage_settings),
        settings=storage_settings,
    )
