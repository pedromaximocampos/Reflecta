import boto3
from mypy_boto3_s3 import S3Client

from src.modules.ai_processing.infrastructure.storage.aws.s3.configs import S3Settings


def make_s3_client(settings: S3Settings) -> S3Client:
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
