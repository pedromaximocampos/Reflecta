import boto3


from src.modules.internal_events.infrastructure.messaging.aws_sns.configs.sns_settings import SNSSettings
from mypy_boto3_sns import SNSClient


def make_sns_client(settings: SNSSettings) -> SNSClient:

    if settings.aws_profile:
        session = boto3.Session(profile_name=settings.aws_profile, region_name=settings.aws_region)
        return session.client(settings.service)

    return boto3.client(settings.service, region_name=settings.aws_region)