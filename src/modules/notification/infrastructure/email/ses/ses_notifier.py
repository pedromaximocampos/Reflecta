import asyncio
import logging

from botocore.exceptions import BotoCoreError, ClientError
from src.modules.notification.domain.ports.isesv2_client import ISESV2Client
from src.modules.notification.application.ports.notifiers.dto import EmailDTO, EmailKind
from src.modules.notification.application.ports.notifiers.iemail_notifier import IEmailNotifier
from src.modules.notification.domain.exceptions.email_notification_errors import (
    PermanentEmailError,
    TransientEmailError,
)
from src.modules.notification.infrastructure.email.templates.password_reset_template_html import (
    PasswordResetTemplateHTML,
)
from src.modules.notification.infrastructure.email.templates.verification_template_html import (
    VerificationTemplateHTML,
)
from src.modules.notification.infrastructure.email.templates.user_deletion_template_html import (
    UserDeletionTemplateHTML,
)
from src.modules.notification.infrastructure.email.templates.user_recovery_template_html import (
    UserRecoveryTemplateHTML,
)


_LOGGER = logging.getLogger(__name__)



class SESNotifier(IEmailNotifier):
    _TRANSIENT_ERROR_CODES = frozenset(
        {
            "InternalServiceErrorException",
            "LimitExceededException",
            "ServiceUnavailableException",
            "ThrottlingException",
            "TooManyRequestsException",
        }
    )

    def __init__(self, client: ISESV2Client, sender_email: str) -> None:
        if not sender_email.strip():
            raise ValueError("SES sender email must not be empty")

        self.__sender = sender_email.strip()
        self.__client = client

    @staticmethod
    def __associate_template(dto: EmailDTO) -> tuple[str, str]:
        if dto.kind is EmailKind.VERIFICATION:
            return (
                VerificationTemplateHTML.get_subject_template(dto),
                VerificationTemplateHTML.get_email_template(dto),
            )
        if dto.kind is EmailKind.PASSWORD_RESET:
            return (
                PasswordResetTemplateHTML.get_subject_template(dto),
                PasswordResetTemplateHTML.get_email_template(dto),
            )
        if dto.kind is EmailKind.USER_DELETION:
            return (
                UserDeletionTemplateHTML.get_subject_template(dto),
                UserDeletionTemplateHTML.get_email_template(dto),
            )
        if dto.kind is EmailKind.USER_RECOVERY:
            return (
                UserRecoveryTemplateHTML.get_subject_template(dto),
                UserRecoveryTemplateHTML.get_email_template(dto),
            )
        raise PermanentEmailError(f"Unsupported email kind: {dto.kind}")

    async def send_email(self, dto: EmailDTO) -> None:
        subject, html_template = self.__associate_template(dto)

        try:
            await asyncio.to_thread(
                self.__client.send_email,
                FromEmailAddress=self.__sender,
                Destination={"ToAddresses": [dto.email.value]},
                Content={
                    "Simple": {
                        "Subject": {
                            "Data": subject,
                            "Charset": "UTF-8",
                        },
                        "Body": {
                            "Html": {
                                "Data": html_template,
                                "Charset": "UTF-8",
                            }
                        },
                    }
                },
            )
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            response_metadata = exc.response.get("ResponseMetadata", {})
            _LOGGER.error(
                "Amazon SES SendEmail failed: error_code=%s http_status=%s request_id=%s",
                error_code or "Unknown",
                response_metadata.get("HTTPStatusCode", "Unknown"),
                response_metadata.get("RequestId", "Unknown"),
            )
            if error_code in self._TRANSIENT_ERROR_CODES:
                raise TransientEmailError("Temporary Amazon SES error") from exc
            raise PermanentEmailError("Amazon SES rejected the email") from exc
        except BotoCoreError as exc:
            _LOGGER.error(
                "Amazon SES client failed: error_type=%s",
                type(exc).__name__,
            )
            raise TransientEmailError("Temporary Amazon SES client error") from exc
