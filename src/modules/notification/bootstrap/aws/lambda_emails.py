import os
import boto3
from src.modules.notification.application.handlers.email_event_handler import EmailEventHandler

from src.modules.notification.infrastructure.email.ses.ses_notifier import SESNotifier
from src.modules.notification.domain.ports.isesv2_client import ISESV2Client


def get_aws_email_handler() -> EmailEventHandler:
    frontend_base_url = os.getenv("FRONTEND_BASE_URL")
    if not frontend_base_url:
        raise ValueError("FRONTEND_BASE_URL environment variable is not set.")
    return EmailEventHandler(
        email_notifier=get_ses_notifier(),
        frontend_base_url=frontend_base_url,
    )



def get_ses_notifier() -> SESNotifier:
    sender = os.getenv("SES_FROM_EMAIL")
    if not sender:
        raise ValueError("SES_FROM_EMAIL environment variable is not set.")
    return SESNotifier(get_ses_provider(), sender)



def get_ses_provider() -> ISESV2Client:

    client = boto3.client('sesv2')

    return client