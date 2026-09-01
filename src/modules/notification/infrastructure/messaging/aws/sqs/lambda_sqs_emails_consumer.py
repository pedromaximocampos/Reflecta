







def lambda_handler(event, context):
    """
    Lambda function to process SQS messages for email notifications.

    Args:
        event (dict): The event data containing SQS messages.
        context (object): The runtime information of the Lambda function.
    """

    for record in event.get('Records', []):
        # Extract the message body from the SQS record
        message_body = record.get('body', {})

        payload = record.get('payload', {})

        if not payload or not message_body:
            raise ValueError("Payload or message body is missing in the SQS record.")

        event_type = payload.get('event_type')
        to = payload.get('user_email')


        # You can add your email sending logic here, for example:
        # send_email(message_body)