import boto3


from src.modules.internal_events.infrastructure.messaging.aws_sqs.configs.sqs_settings import SQSSettings
from mypy_boto3_sqs import SQSClient

def make_sqs_client(settings: SQSSettings) -> SQSClient:

    if settings.aws_profile:
        session = boto3.Session(profile_name=settings.aws_profile, region_name=settings.aws_region)
        return session.client(settings.service)

    return boto3.client(settings.service, region_name=settings.aws_region)
