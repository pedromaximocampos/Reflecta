from abc import  ABC, abstractmethod
from typing import Any
from email.message import EmailMessage
import aiosmtplib
from src.core.settings import get_settings

_settings = get_settings()

class BaseSMTPEmailNotifier(ABC):

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.__smtp_server = smtp_server
        self.__smtp_port = smtp_port
        self.__username = username
        self.__password = password
        self._domain = _settings.FRONT_END_DOMAIN
        self._app_name = _settings.APP_NAME
        self._from = f"{self._app_name} <no-reply@{self._domain}>"


    async def _send(self, message: EmailMessage) -> None:
        await aiosmtplib.send(
            message,
            hostname=self.__smtp_server,
            port=self.__smtp_port,
            username=self.__username,
            password=self.__password,
            start_tls=True,
        )

    @abstractmethod
    async def send_email(self, dto: Any) -> None:
        ...


    @abstractmethod
    def get_template(self, dto) -> str:
        ...

    @abstractmethod
    def get_subject(self) -> str:
        ...