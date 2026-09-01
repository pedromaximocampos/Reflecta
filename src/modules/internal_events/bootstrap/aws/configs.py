from src.modules.internal_events.infrastructure.messaging.aws_sns.configs.sns_settings import SNSSettings
from src.modules.internal_events.infrastructure.messaging.aws_sqs.configs.sqs_settings import SQSSettings
from src.shared.config.settings import get_settings

_SETTINGS = get_settings()


def get_sqs_emails_settings() -> SQSSettings:
    return SQSSettings(
        aws_region=_SETTINGS.AWS_SQS_REGION,
        aws_profile=_SETTINGS.AWS_PROFILE,
        queue_url=_SETTINGS.AWS_SQS_EMAILS_QUEUE_URL,
    )


def get_sns_publishers_settings() -> SNSSettings:
    return SNSSettings(
        aws_region=_SETTINGS.AWS_SNS_REGION,
        aws_profile=_SETTINGS.AWS_PROFILE,
        sns_arn=_SETTINGS.AWS_SNS_ARN,
    )