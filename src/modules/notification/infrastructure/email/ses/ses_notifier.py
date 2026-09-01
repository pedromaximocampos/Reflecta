from mypy_boto3_sqs import SQSClient, Client

from modules.notification.application.ports.notifiers.dto import EmailDTO
from src.modules.notification.application.ports.notifiers.iemail_notifier import IEmailNotifier


class SESNotifier(IEmailNotifier):

    def __init__(self, client: Client, sender_email: str) -> None:
        self.__sender = sender_email
        self.__client = client


    async def send_email(self, dto: EmailDTO) -> None:
        response = self.__client.send_email(