import boto3
from mypy_boto3_sqs import SQSClient

from src.modules.ai_processing.infrastructure.messaging.aws_sqs.configs import (
    WorkIngestionSQSSettings,
)


def make_sqs_client(settings: WorkIngestionSQSSettings) -> SQSClient:
    client_options = {
        "region_name": settings.aws_region,
        "endpoint_url": settings.endpoint_url,
    }
    if settings.aws_profile:
        session = boto3.Session(
            profile_name=settings.aws_profile,
            region_name=settings.aws_region,
        )
        return session.client(settings.service, **client_options)
    return boto3.client(settings.service, **client_options)
