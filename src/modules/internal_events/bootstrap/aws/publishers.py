from modules.internal_events.infrastructure.messaging.aws_sns.publishers.base_sns_publisher import BaseSnsPublisher
from src.modules.internal_events.infrastructure.messaging.aws_sqs.publishers.emails_sqs_publisher import EmailSQSPublisher
from src.modules.internal_events.bootstrap.aws.configs import get_sqs_emails_settings, get_sns_publishers_settings


def get_emails_sqs_publishers() -> EmailSQSPublisher:

    return EmailSQSPublisher(
        sqs_settings=get_sqs_emails_settings()
    )


def get_sns_publisher():
    return BaseSnsPublisher(
        sns_configs=get_sns_publishers_settings(),
    )