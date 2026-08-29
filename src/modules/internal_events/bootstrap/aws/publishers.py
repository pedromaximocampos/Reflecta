from src.modules.internal_events.infrastructure.messaging.aws_sqs.publishers.emails_sqs_publisher import EmailSQSPublisher
from src.modules.internal_events.bootstrap.aws.configs import get_sqs_emails_settings


def get_emails_sqs_publishers() -> EmailSQSPublisher:

    return EmailSQSPublisher(
        sqs_settings=get_sqs_emails_settings()
    )