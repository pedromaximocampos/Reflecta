from src.application.ports.emails.dto import EmailVerificationDTO
from src.application.ports.emails.iemail_verification_notifier import IEmailVerificationNotifier
from src.infra.messaging.rabbitmq.base_rabbitmq_consumer_worker import BaseRabbitMQConsumerWorker
from src.infra.messaging.rabbitmq.configs.settings import RabbitMQConsumerConfig


class EmailVerificationConsumerWorker(BaseRabbitMQConsumerWorker):

    def __init__(self, consumer_config: RabbitMQConsumerConfig, email_verification_notifier: IEmailVerificationNotifier):
        super().__init__(consumer_config)
        self.__email_verification_notifier = email_verification_notifier


    async def handle_message(self, payload: dict):
        verification_dto  = self.__return_email_verification_dto(payload)

        await self.__email_verification_notifier.send_email(verification_dto)


    @staticmethod
    def __return_email_verification_dto(payload: dict) -> EmailVerificationDTO:
        raw_token = payload.get("raw_code")
        user_email = payload.get("user_email")
        expires_in = payload.get("expires_in")
        verification_url = payload.get("verification_url")
        user_name = payload.get("user_name")

        return EmailVerificationDTO(
            email=user_email,
            raw_code=raw_token,
            expires_in_minutes=expires_in,
            user_name=user_name,
            verification_link=verification_url
        )

