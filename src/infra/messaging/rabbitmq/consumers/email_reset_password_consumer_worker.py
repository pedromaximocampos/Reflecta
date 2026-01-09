from src.application.ports.emails.dto import EmailPasswordResetDTO
from src.application.ports.emails.iemail_password_reset_notifier import IEmailPasswordResetNotifier
from src.domain.value_objects.email import Email
from src.infra.messaging.rabbitmq.consumers.base_rabbitmq_consumer_worker import BaseRabbitMQConsumerWorker
from src.infra.messaging.rabbitmq.configs.settings import RabbitMQConsumerConfig


class EmailPasswordResetConsumerWorker(BaseRabbitMQConsumerWorker):

    def __init__(self, consumer_config: RabbitMQConsumerConfig, email_password_reset_notifier: IEmailPasswordResetNotifier):
        super().__init__(consumer_config)
        self.__email_password_reset_notifier = email_password_reset_notifier


    async def handle_message(self, payload: dict):
        password_reset_dto  = self.__return_email_password_reset_dto(payload)

        await self.__email_password_reset_notifier.send_email(password_reset_dto)


    @staticmethod
    def __return_email_password_reset_dto(payload: dict) -> EmailPasswordResetDTO:
        return EmailPasswordResetDTO(
            email=Email(payload.get("user_email")),
            raw_code=payload.get("raw_code"),
            expires_in_minutes=payload.get("expires_in"),
            username=payload.get("username"),
            reset_password_link=payload.get("reset_password_link"))