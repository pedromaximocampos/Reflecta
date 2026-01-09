from abc import  ABC, abstractmethod
from typing import Any
from email.message import EmailMessage
import aiosmtplib

from src.domain.exceptions.custom_exceptions.emails_notification_erros import TransientEmailError, PermanentEmailError
from aiosmtplib.errors import (
    SMTPConnectError,
    SMTPServerDisconnected,
    SMTPTimeoutError,
    SMTPRecipientsRefused,
    SMTPResponseException,
)

from src.infra.email.smtp.configs.settings import SMTPSettings


class BaseSMTPEmailNotifier(ABC):

    def __init__(self, smtp_config: SMTPSettings) -> None:
        self._config = smtp_config


    async def _send(self, message: EmailMessage) -> None:

        try:
            await aiosmtplib.send(
                message,
                hostname=self._config.server,
                port=self._config.port,
                username=self._config.username,
                password=self._config.password,
                start_tls=True,
            )
        except (
                SMTPConnectError,
                SMTPServerDisconnected,
                SMTPTimeoutError,
                TimeoutError,
                ConnectionError,
            ) as exc:
            raise TransientEmailError("Temporary SMTP error") from exc


        except SMTPResponseException as exc:
            if 400 <= exc.code < 500:
                raise TransientEmailError(f"SMTP temporary error ({exc.code})") from exc
            else:
                raise PermanentEmailError(f"SMTP permanent error ({exc.code})") from exc

        except SMTPRecipientsRefused as exc:
            raise PermanentEmailError("Invalid recipient email address") from exc

        except Exception as exc:
            raise PermanentEmailError("SMTP authentication failed") from exc

    @abstractmethod
    async def send_email(self, dto: Any) -> None:
        ...


    @abstractmethod
    def get_template(self, dto) -> str:
        ...

    @abstractmethod
    def get_subject(self) -> str:
        ...