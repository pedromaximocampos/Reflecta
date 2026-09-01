import asyncio
import json
import os

import boto3

from src.modules.notification.domain.value_objects.emails_event_types import EmailsEventType
from src.modules.notification.application.handlers.email_event_handler import EmailEventHandler
from src.modules.notification.infrastructure.email.ses.ses_notifier import SESNotifier

client = boto3.client('sesv2')
sender = os.getenv("SES_FROM_EMAIL")

if not sender:
    raise ValueError("SES_FROM_EMAIL environment variable is not set.")

notifier_ses = SESNotifier(client, sender)
email_handler = EmailEventHandler(
    email_notifier=notifier_ses,
    frontend_base_url=os.getenv("FRONTEND_BASE_URL", "http://localhost:8000")
)


async def process_record(record: dict):
    message_body = record.get("body", "")
    payload = json.loads(message_body)
    message_attributes = record.get('messageAttributes', {})

    if not payload or not message_body:
        raise ValueError("Payload or message body is missing in the SQS record.")

    try:
        event_type = EmailsEventType(message_attributes.get('event_type', {}).get('stringValue', ''))
    except ValueError as e:
        raise ValueError(f"Invalid event type: {payload.get('event_type')}") from e

    await email_handler.handle(event_type, payload)


async def process_batch(records: list):
    failures = []
    for record in records:
        try:
            await process_record(record)
        except Exception as e:
            print(f"Error processing record {record.get('messageId')}: {e}")
            failures.append({
                "itemIdentifier": record.get('messageId'),

            })
    return  { "batchItemFailures": failures }


def lambda_handler(event, context):
    """
    Lambda function to process SQS messages for email notifications.

    Args:
        event (dict): The event data containing SQS messages.
        context (object): The runtime information of the Lambda function.
    """
    records = event.get('Records', [])
    return asyncio.run(process_batch(records))
