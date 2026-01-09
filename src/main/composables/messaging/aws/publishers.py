from src.infra.messaging.aws_sqs.publishers.emails_sqs_publisher import EmailSQSPublisher
from src.main.composables.messaging.aws.configs import get_sqs_emails_settings


def get_emails_sqs_publishers() -> EmailSQSPublisher:

    return EmailSQSPublisher(
        sqs_settings=get_sqs_emails_settings()
    )