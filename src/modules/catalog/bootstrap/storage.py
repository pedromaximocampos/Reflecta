from src.modules.catalog.application.ports.storage.iwork_document_storage import (
    IWorkDocumentStorage,
)
from src.modules.catalog.infrastructure.storage.aws.s3.clients.s3_client import (
    make_s3_client,
)
from src.modules.catalog.infrastructure.storage.aws.s3.configs.s3_settings import (
    S3Settings,
)
from src.modules.catalog.infrastructure.storage.aws.s3.work_document_storage import (
    S3WorkDocumentStorage,
)
from src.shared.config.settings import get_settings


def get_work_document_storage() -> IWorkDocumentStorage:
    application_settings = get_settings()
    s3_settings = S3Settings(
        aws_region=application_settings.AWS_S3_REGION,
        bucket_name=application_settings.AWS_S3_WORKS_BUCKET,
        aws_profile=application_settings.AWS_PROFILE,
    )
    return S3WorkDocumentStorage(
        client=make_s3_client(s3_settings),
        settings=s3_settings,
    )
