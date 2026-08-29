from src.modules.internal_events.infrastructure.messaging.aws_sqs.configs.sqs_settings import SQSSettings
from src.main.composables.shared.settings import _SETTINGS



def get_sqs_emails_settings() -> SQSSettings:
    return SQSSettings(
        aws_region=_SETTINGS.AWS_SQS_REGION,
        aws_profile=_SETTINGS.AWS_PROFILE,
        queue_url=_SETTINGS.AWS_SQS_EMAILS_QUEUE_URL,
    )